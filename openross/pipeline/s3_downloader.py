from twisted.internet import defer, threads, task, reactor
from twisted.python import log
from datetime import datetime
from errors import NoDataInS3Error
from utils import time_on_statsd, statsd_name
from txaws.service import AWSServiceRegion
from txaws.regions import S3_EU_WEST
import boto
import settings
import logging


class S3Downloader(object):
    """ Pipeline process which downloads a media file from S3 """

    def __init__(self, engine):
        self.engine = engine
        self.s3conn = boto.connect_s3(
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
        )
        self.txs3conn = AWSServiceRegion(
            access_key=settings.AWS_ACCESS_KEY_ID,
            secret_key=settings.AWS_SECRET_ACCESS_KEY,
            s3_uri=S3_EU_WEST[0]['endpoint'],
        ).get_s3_client()
        self.botobucket = self.s3conn.get_bucket(settings.IMAGES_STORE)

    @defer.inlineCallbacks
    def _get_data_from_s3_tx(self, path):
        """ txAWS GET from S3 """
        image = yield self.txs3conn.get_object(
            settings.IMAGES_STORE,
            str(path),
        )
        defer.returnValue(image)

    def _get_data_from_s3(self, path):
        """ boto GET from S3 """
        key = self.botobucket.get_key(path)
        data = key.get_contents_as_string()
        return data

    @time_on_statsd(statsd_name(), 's3_downloader')
    def process_image(self, payload,  **kwargs):
        """ Gets image data from S3.
            This attempts to download from s3 settings.ATTEMPTS times and timeouts after
            settings.S3_TIMEOUT """

        def _create_deferred(timeout=0):
            """ Creates a deferred which will run after a given delay """
            if settings.USE_BOTO:
                dfd = task.deferLater(
                    reactor, timeout,
                    threads.deferToThread, self._get_data_from_s3, payload['image_path']
                )
            else:
                dfd = task.deferLater(
                    reactor, timeout, self._get_data_from_s3_tx, payload['image_path']
                )
                return dfd

        def _s3callback(deferred_list_result):
            """ When one of the requests has completed, cancel the rest """

            [dfd.cancel() for dfd in dfds_list if not dfd.called]
            if not deferred_list_result[0]:
                raise NoDataInS3Error()
            payload['original_image'] = deferred_list_result[0]
            return payload

        def _timeout_and_fail(dfds_list):
            """ If none of the defers has finished by (attempts+1)*timeout then
                cancel and return an error """

            [dfd.cancel() for dfd in dfds_list if not dfd.called]

        def _surpress_cancel_error(result):
            if isinstance(result, defer.CancelledError):
                pass

        # Skip if already exists from cache
        if 'original_image' in payload.keys():
            return payload

        if settings.DEBUG:
            log.msg(
                "[%s] Starting S3 Download" % datetime.now().isoformat(), logLevel=logging.DEBUG
            )

        # Make a deferred list of download attempts that have their predefined starting
        # times baked into the deferred. Return when any deferred has a successful result
        # Keep a list of the original deferred as we cannot access them once in DeferredList
        dfds_list = []
        for attempt in range(0, settings.S3_ATTEMPTS):
            dfds_list.append(_create_deferred(timeout=attempt*settings.S3_TIMEOUT))
            dfds_list[-1].addErrback(_surpress_cancel_error)
        dfds = defer.DeferredList(dfds_list, fireOnOneCallback=True)
        dfds.addCallback(_s3callback)

        # Auto cancel requests which don't fire after their max timeout
        reactor.callLater(
            settings.S3_ATTEMPTS*settings.S3_TIMEOUT, _timeout_and_fail, dfds_list
        )

        return dfds
