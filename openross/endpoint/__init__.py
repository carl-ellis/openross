import engine
from twisted.python import log
from twisted.web import resource, server
from endpoint.healthcheck import healthcheck
from errors import NoDataInS3Error
import settings
import logging
import utils


class BobRossEndpoint(resource.Resource):
    isLeaf = True
    engine = engine.BobRossEngine()

    def _process_image(self, image_path, width, height, mode, **kwargs):
        """ Adds a new image to the resizer engine. Will return deferred """

        if settings.DEBUG:
            log.msg(
                'Received new image, url:%s, w:%s, h:%s, m:%s kw:%s' % (
                    image_path, width, height, mode, kwargs),
                logLevel=logging.DEBUG
            )

        payload = {}
        payload['image_path'] = image_path
        payload['width'] = width
        payload['height'] = height
        payload['mode'] = mode
        payload['timers'] = {}
        if width == '-1' and height == '-1':
            payload['skip_resize'] = True

        return BobRossEndpoint.engine.process_image(payload, **kwargs)

    def _check_allowed_size(self, width, height, mode):
        """ Check if requested size is in settings """

        if int(width) <= settings.MAX_SIZE[0] and int(height) <= settings.MAX_SIZE[1]:
            if settings.USE_WHITELIST:
                if width in settings.IMAGE_WHITELIST.keys():
                    if height in settings.IMAGE_WHITELIST[width]:
                        if mode in settings.ALLOWED_MODES:
                            return True
                return False
            else:
                return True
        else:
            return False

    def render_GET(self, request):
        """ Handle GET request to server """

        def on_finish(data, request):
            if settings.DEBUG:
                log.msg("Header Info: %s" % data, logLevel=logging.DEBUG)
            request.setHeader('X-Accel-Redirect', data)
            request.setHeader('Content-Type', 'image/jpeg')
            request.finish()

        def on_error(data):
            if settings.DEBUG:
                log.msg('Error: %s' % data, logLevel=logging.DEBUG)

            # Reraise exception to send to Sentry
            try:
                data.raiseException()
            except NoDataInS3Error:
                utils.capture_warning(
                    'No Data in S3 Key',
                    extra={
                        'key': image_path,
                    }
                )
            except:
                utils.capture_exception(
                    extra={
                        'key': image_path, 'width': width, 'height': height, 'mode': mode
                    }
                )
            request.setResponseCode(403)
            request.finish()

        width = None
        height = None
        mode = None
        image_path = None

        if request.path and request.args:
            if ('width' in request.args.keys()
                and 'height' in request.args.keys()
                    and 'mode' in request.args.keys()):

                width = request.args.pop('width')[0]
                height = request.args.pop('height')[0]
                mode = request.args.pop('mode')[0]
                image_path = request.path
        elif request.path:
                image_path = request.path

        # Check for valid size
        if width and height and mode and not self._check_allowed_size(width, height, mode):
            if settings.DEBUG:
                log.msg(
                    "Size isn't white listed: (%s, %s)" % (width, height), logLevel=logging.DEBUG
                )
            request.setResponseCode(403)
            return ''

        # If size is not defined, skip resizing and fill in payload magic numbers
        if not width and not height and not mode:
            width = '-1'
            height = '-1'
            mode = 'resize'

        # Strip leading /
        if image_path[0] == '/':
            image_path = image_path[1:]

        # If request if for /health, run a sanity test with known input and test against
        # expected output
        if request.path == settings.HEALTH_CHECK_PATH:
            healthcheck(request, BobRossEndpoint.engine)
            return server.NOT_DONE_YET

        # Ensure image is a jpeg that is being requested
        if '.jpeg' not in request.path and '.jpg' not in request.path:
            request.setResponseCode(403)
            return ''

        d = self._process_image(image_path, width, height, mode, **request.args)
        d.addCallback(on_finish, request)
        d.addErrback(on_error)
        return server.NOT_DONE_YET
