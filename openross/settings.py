DEBUG = False
USE_BOTO = False

IMAGE_PROCESSOR = 'pipeline.ImagePipelineManager'
IMAGE_PIPELINES = [
    'pipeline.cache_check.CacheCheck',
    'pipeline.s3_downloader.S3Downloader',
    'pipeline.resizer.Resizer',
    'pipeline.cacher.Cacher',
]

THREAD_POOL_SIZE = 8

SENTRY_DSN = ''
STATSD_HOST = 'localhost'
STATSD_PORT = 8125
STATSD_NAME = 'bobross'

IMAGES_STORE = ''

# AWS creds - Ensure these are overwritten in your local settings file
AWS_ACCESS_KEY_ID = None
AWS_SECRET_ACCESS_KEY = None

# Will essentially give the first deferred 600ms to finish, second 400ms, etc
S3_TIMEOUT = 0.2
S3_ATTEMPTS = 3

CACHE_LOCATION = ''
WEB_CACHE_LOCATION = ''

# Add an image whitelist to stop attacks on service
USE_WHITELIST = False
MAX_SIZE = (2000, 2000)
IMAGE_WHITELIST_SETTING = [
    ('-1', '-1'),  # For passthrough
    ('72', '72'),
    ('200', '250'),
    ('1024', '768'),
]

# Turn the above human readable white list into an efficient lookup table
IMAGE_WHITELIST = {}
for size in IMAGE_WHITELIST_SETTING:
    if size[0] in IMAGE_WHITELIST.keys():
        IMAGE_WHITELIST[size[0]].append(size[1])
    else:
        IMAGE_WHITELIST[size[0]] = [size[1]]
for key in IMAGE_WHITELIST.keys():
    IMAGE_WHITELIST[key] = set(IMAGE_WHITELIST[key])

ALLOWED_MODES = [
    'resize',
    'resizecomp',
    'crop',
    'trimresize',
]

# Health check info - Ensure these are overwritten in your local settings file
HEALTH_CHECK_PATH = '/health'
HEALTH_CHECK_IMAGE_PATH = ''
HEALTH_CHECK_IMAGE_WIDTH = ''
HEALTH_CHECK_IMAGE_HEIGHT = ''

HEALTH_EXPECTED_SIZE = {
    'resize': (1, 1),
    'resizecomp': (1, 1),
    'crop': (1, 1),
    'trimresize': (1, 1),
}

# Read settings from ~/.openross.py for private settings such as KEYS
import os.path
import sys
CONFIG_FILE = os.path.abspath(os.path.expanduser("~/.openross.py"))
if os.path.exists(CONFIG_FILE):
    import imp
    mod = imp.new_module('tmp_config')
    try:
        execfile(CONFIG_FILE, mod.__dict__)
        sys.modules[mod.__name__] = mod
        from tmp_config import *
    except:
        sys.stderr.write("Couldn't load configuration file\n")
        import traceback
        traceback.print_exc()
        raise
