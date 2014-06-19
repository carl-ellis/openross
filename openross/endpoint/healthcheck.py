from twisted.internet import defer
import settings


def _healthcheck_process_image(engine, image_path, width, height, mode, **kwargs):
    """ Build a payload for a healthcheck """
    payload = {}
    payload['image_path'] = image_path
    payload['width'] = width
    payload['height'] = height
    payload['mode'] = mode
    if width == '-1' and height == '-1':
        payload['skip_resize'] = True

    return engine.health_check_image(payload, **kwargs)


def healthcheck(request, engine):
    """ Handles the health check process.
        This puts a predefined image through the pipeline for each mode, ensures there
        is no error, and ensures the sizes are expected
    """

    def on_health_finish(data, request):
        """ Result of health check. Res is a TextTestResult object """
        for res in data:
            # res format is (Success?, result)
            if not res[0]:
                request.setResponseCode(500)
                request.finish()
                return

        request.write('OK')
        request.setResponseCode(200)
        request.finish()

    width = settings.HEALTH_CHECK_IMAGE_WIDTH
    height = settings.HEALTH_CHECK_IMAGE_HEIGHT
    image_path = settings.HEALTH_CHECK_IMAGE_PATH
    modes = settings.ALLOWED_MODES

    dfd = defer.DeferredList(
        [_healthcheck_process_image(engine, image_path, width, height, m, **request.args)
            for m in modes]
    )
    dfd.addBoth(on_health_finish, request)
