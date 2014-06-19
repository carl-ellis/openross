from twisted.trial import unittest
from twisted.internet import defer
from pipeline.cacher import Cacher
import os
import engine
import test_settings


class TestCacher(unittest.TestCase):

    def setUp(self):
        self.testpayload = {
            'width' : '200',
            'height' : '200',
            'mode' : 'resize',
            'image_path': 'test.jpeg',
            'image': 'test',
            'original_image': 'test',
        }
        self.testlocation = '%s/%s' % (
            test_settings.CACHE_LOCATION, 'test_200x200_resize.jpeg')

        self.testpayload_original = {
            'width' : '-1',
            'height' : '-1',
            'mode' : 'r',
            'image_path': 'test.jpeg',
            'image': 'test',
            'original_image': 'test',
            'skip_resize': True,
        }
        self.testlocation_original = '%s/%s' % (test_settings.CACHE_LOCATION, 'test.jpeg')

    def tearDown(self):
        if os.path.exists(self.testlocation):
            os.remove(self.testlocation)
        if os.path.exists(self.testlocation_original):
            os.remove(self.testlocation_original)

    @defer.inlineCallbacks
    def test_cache_write_normal(self):
        """ Test cacher pipeline for normal file
        """
        cacher = Cacher(engine.BobRossEngine())
        import settings
        settings.CACHE_LOCATION = test_settings.CACHE_LOCATION + '/'

        yield cacher.process_image(self.testpayload)
        self.assertTrue(os.path.exists(self.testlocation), True)

    @defer.inlineCallbacks
    def test_cache_write_original(self):
        """ Test cacher pipeline for normal file
        """
        cacher = Cacher(engine.BobRossEngine())
        import settings
        settings.CACHE_LOCATION = test_settings.CACHE_LOCATION + '/'

        yield cacher.process_image(self.testpayload_original)
        self.assertTrue(os.path.exists(self.testlocation_original), True)

