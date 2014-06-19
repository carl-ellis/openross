import pgmagick as pg

""" This Module is where image processing functions are defined.
    It will contain a mapping between mode and processing functions
"""


_mode_map = {}  # Mode register


def process_image_with_mode(img, width, height, mode):
    """ Public way of accessing image processing mode """
    return _mode_map[mode](img, width, height)


def _register_mode(mode_name, func):
    """ Register a mode with the module """
    global _modemap
    _mode_map[mode_name] = func


def _resize(img, width, height):
    """ Used to be called 'reflow'
        This:
          Performs a box resize on the original image
        Mode key: 'r'
    """

    img.scale('%sx%s' % (width, height))

    return img


def _resizecomp(img, width, height):
    """ Used to be called 'normal'
        This:
          First performs a box resize on the original image
          Secondly, composites the image on to a white square of the required wxh
        Mode key: 'resizecomp'
    """

    img.scale('%sx%s' % (width, height))

    backdrop = pg.Image(pg.Geometry(int(width), int(height)), 'white')
    wdiff = (int(width) - img.size().width()) / 2
    hdiff = (int(height) - img.size().height()) / 2
    backdrop.composite(img, wdiff, hdiff, pg.CompositeOperator.AtopCompositeOp)
    img = backdrop

    return img


def _crop(img, width, height):
    """ This:
          First performs a box resize on the original image, but so only the smallest
            dimension is in the box. So if width was smaller, the image would be resized
            to Wx?
          Secondly, The image is cropped to the desired size, trimming the edges that are
            outside of the box
        Mode key: 'crop'
    """

    if img.size().width() < img.size().height():
        img.scale('%sx999999' % (width))
    else:
        img.scale('999999x%s' % (height))

    backdrop = pg.Image(pg.Geometry(int(width), int(height)), 'white')
    wdiff = (img.size().width() - int(width)) / 2
    hdiff = (img.size().height() - int(height)) / 2
    backdrop.composite(img, -wdiff, -hdiff, pg.CompositeOperator.CopyCompositeOp)
    img = backdrop

    return img


def _trim_resize(img, width, height):
    """ This:
          First performs a trim on the image with no color fuzz
          Secondly, performs a box resize on the original image only if the image is larger
            than the target size
          Thirdly, composites the image on to a white square of the required wxh
        Mode key: 'trimresize'
    """

    img.trim()

    w, h = img.size().width(), img.size().height()
    if w > int(width) or h > int(height):
        img.scale('%sx%s' % (width, height))

    backdrop = pg.Image(pg.Geometry(int(width), int(height)), 'white')
    wdiff = (int(width) - img.size().width()) / 2
    hdiff = (int(height) - img.size().height()) / 2
    backdrop.composite(img, wdiff, hdiff, pg.CompositeOperator.AtopCompositeOp)
    img = backdrop

    return img


# mode registrations
_register_mode('resize', _resize)
_register_mode('resizecomp', _resizecomp)
_register_mode('crop', _crop)
_register_mode('trimresize', _trim_resize)
