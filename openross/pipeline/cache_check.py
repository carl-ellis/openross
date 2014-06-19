from twisted.internet import defer, threads
from twisted.python import log
from utils import time_on_statsd, statsd_name
import settings
import glob
import os
import logging


class CacheCheck(object):
    """ Pipeline process which checks if an image already exists in the cache that can
        be resized, rather than hitting S3 """

    def __init__(self, engine):
        self.engine = engine

    def _find_cache_matches(self, file_path):
        """ Look for a file (no resized, original s3 download) in the cache """

        orig_format = '%s.jpeg' % file_path[:-1]
        for f in glob.iglob(orig_format):
            if f == orig_format:
                return f
        return False

    def _read_image(self, file_path):
        """ Read file from filesystem """

        with open(file_path, 'r') as image:
            return image.read()

    @time_on_statsd(statsd_name(), 'cache_check')
    @defer.inlineCallbacks
    def process_image(self, payload, **kwargs):
        """ Checks the cache for a suitable source image
            This allows S3 to be skipped
        """

        filecache_loc = settings.CACHE_LOCATION
        filefront = payload['image_path'].split('.')[0]
        file_cache = "%s*" % os.path.join(filecache_loc, filefront)

        bigger_cache = self._find_cache_matches(file_cache)

        if not bigger_cache:
            defer.returnValue(payload)

        if settings.DEBUG:
            log.msg(
                'Original file found in cache, skipping S3: %s' % (bigger_cache),
                logLevel=logging.DEBUG)

        data = yield threads.deferToThread(self._read_image, bigger_cache)
        payload['original_image'] = data

        defer.returnValue(payload)
