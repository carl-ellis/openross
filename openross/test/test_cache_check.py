import unittest
import engine
import test_settings
import os
from pipeline.cache_check import CacheCheck


class TestCacheCheck(unittest.TestCase):

    def setUp(self):
        self.testfile_original = '%s/%s' % (test_settings.CACHE_LOCATION, 'image.jpeg')
        print self.testfile_original
        open(self.testfile_original, 'a').close()

    def tearDown(self):
        if os.path.exists(self.testfile_original):
            os.remove(self.testfile_original)

    def test_cache_has_original_image(self):
        cachec = CacheCheck(engine.BobRossEngine())
        import settings
        settings.CACHE_LOCATION = test_settings.CACHE_LOCATION + '/'

        test_file_path = '%s/%s' % (test_settings.CACHE_LOCATION, 'image*')
        cache_file_path = cachec._find_cache_matches(test_file_path)
        self.assertEqual(cache_file_path, self.testfile_original)

        test_file_path = '%s/%s' % (test_settings.CACHE_LOCATION, 'image2*')
        cache_file_path = cachec._find_cache_matches(test_file_path)
        self.assertEqual(cache_file_path, False)
