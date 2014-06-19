from twisted.internet import defer
from twisted.internet import fdesc
from twisted.python import log
from datetime import datetime
from utils import time_on_statsd, statsd_name
import settings
import os
import logging


class Cacher(object):
    """ Pipeline process which caches original and resized image into local cache """

    def __init__(self, engine):
        self.engine = engine

    @time_on_statsd(statsd_name(), 'cacher')
    @defer.inlineCallbacks
    def process_image(self, payload, **kwargs):
        """ Writes images to the cache """

        filecache_loc = settings.CACHE_LOCATION
        webcache_loc = settings.WEB_CACHE_LOCATION
        cache_filename_parts = payload['image_path'].split('.')
        filefront = cache_filename_parts[0]
        fileend = cache_filename_parts[1]
        cache_filename = ''

        original_filename = '%s.%s' % (
            filefront,
            fileend,
        )
        cache_filename = '%s_%sx%s_%s.%s' % (
            filefront,
            payload['width'],
            payload['height'],
            payload['mode'],
            fileend,
        )

        file_cache = os.path.join(filecache_loc, cache_filename)
        web_cache = os.path.join(webcache_loc, cache_filename)

        # Files are normally binned in subdir, create them in cache
        dirs = os.path.dirname(file_cache)
        try:
            os.makedirs(dirs)
        except os.error:
            pass

        if 'skip_resize' in payload.keys():
            # Just save/servwe original image as there is no resized image
            file_cache = os.path.join(filecache_loc, original_filename)
            web_cache = os.path.join(webcache_loc, original_filename)

        # Save image to be served
        fd = open(file_cache, 'w')
        fdesc.setNonBlocking(fd.fileno())
        yield fdesc.writeToFD(fd.fileno(), payload['image'])
        fd.close()

        if 'skip_resize' not in payload.keys():
            # If image to be served has beenr esized, also cache full size image
            file_cache = os.path.join(filecache_loc, original_filename)
            fd = open(file_cache, 'w')
            fdesc.setNonBlocking(fd.fileno())
            yield fdesc.writeToFD(fd.fileno(), payload['original_image'])
            fd.close()

        if settings.DEBUG:
            log.msg(
                "[%s] Cached image location: %s" % (datetime.now().isoformat(), file_cache),
                logLevel=logging.DEBUG
            )

        defer.returnValue(web_cache)
