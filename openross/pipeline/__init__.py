from middleware import MiddlewareManager


class ImagePipelineManager(MiddlewareManager):
    """ Builds the image pipeline given configured elements """

    component_name = 'image pipeline'

    @classmethod
    def _get_mwlist_from_settings(cls, settings):
        return settings.IMAGE_PIPELINES

    def _add_middleware(self, pipe):
        super(ImagePipelineManager, self)._add_middleware(pipe)

        if hasattr(pipe, 'process_image'):
            self.methods['process_image'].append(pipe.process_image)

    def process_image(self, payload, **kwargs):
        """Process image. kwargs should always have an image, width, and height"""
        return self._process_chain('process_image', payload, **kwargs)
