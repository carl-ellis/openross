from twisted.python.failure import Failure
from twisted.python import log
from twisted.internet import defer
import utils
import settings
import logging
import statsd


class BobRossEngine(object):
    """ Main class providing image processing for json calls """

    def __init__(self):
        imageproc_cls = utils.load_object(settings.IMAGE_PROCESSOR)
        self.imageproc = imageproc_cls.from_settings(settings, self)
        statsd.Connection.set_defaults(host=settings.STATSD_HOST,
                                       port=settings.STATSD_PORT,
                                       sample_rate=1)

    def process_image(self, payload, **kwargs):
        """ Start image pipeline and return deferred"""

        dfd = self.imageproc.process_image(payload, **kwargs)
        dfd.addBoth(self._imageproc_finished, payload, **kwargs)
        return dfd

    def health_check_image(self, payload, **kwargs):
        """ Health check needs a different succeed/fail check than the normal pipeline
        """

        def _healthcheck_finished(output, payload, **kwargs):
            """ Callback to ensure size is what is expected """
            if isinstance(output, Failure):
                return defer.fail(output)
            else:
                required_size = settings.HEALTH_EXPECTED_SIZE[payload['mode']]
                if payload['resized_width'] == required_size[0] \
                        and payload['resized_height'] == required_size[1]:
                    return defer.succeed(output)
                else:
                    return defer.fail()

        d = self.imageproc.process_image(payload, **kwargs)
        d.addBoth(_healthcheck_finished, payload, **kwargs)
        return d

    def _imageproc_finished(self, output, payload, **kwargs):
        """Processing of images leaving the pipeline """
        if isinstance(output, Failure):
            if settings.DEBUG:
                log.err(
                    'Error Processing %s' % payload['image_path'], logLevel=logging.ERROR)
            return defer.fail(output)
        else:
            if settings.DEBUG:
                log.msg('IMG: %s - done' % payload['image_path'])
            return defer.succeed(output)
