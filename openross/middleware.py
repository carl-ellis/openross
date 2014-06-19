from collections import defaultdict
from twisted.internet import defer
from twisted.python import log
import utils


def process_chain(callbacks, input, *a, **kw):
    """ Return a deferred built by chaining callbacks"""
    d = defer.Deferred()
    for x in callbacks:
        d.addCallback(x, *a, **kw)
    d.callback(input)
    return d


class NotConfigured(Exception):
    """Indiciates a missing configuration situation"""
    pass


class MiddlewareManager(object):

    component_name = 'base middleware'

    def __init__(self, *middlewares):
        self.middlewares = middlewares
        self.methods = defaultdict(list)
        for mw in middlewares:
            self._add_middleware(mw)

    @classmethod
    def _get_mwlist_from_settings(cls, settings):
        """ Get middle ware pipeline settings """
        raise NotImplementedError

    @classmethod
    def from_settings(cls, settings, engine):
        """ Build middleware pipeline from settings """
        mwlist = cls._get_mwlist_from_settings(settings)
        middlewares = []
        for clspath in mwlist:
            try:
                mwcls = utils.load_object(clspath)
                if hasattr(mwcls, 'from_settings'):
                    mw = mwcls.from_settings(settings, engine)
                else:
                    mw = mwcls(engine)
                middlewares.append(mw)
            except NotConfigured, e:
                if e.args:
                    clsname = clspath.split('.')[-1]
                    log.msg('Disabled %s: %s' % (clsname, e.args[0]))
        enabled = [x.__class__.__name__ for x in middlewares]
        log.msg('Enabled %ss: %s' % (cls.component_name, ', '.join(enabled)))
        return cls(*middlewares)

    def _add_middleware(self, pipe):
        """ by default do nothing """
        pass

    def _process_chain(self, methodname, obj, *args):
        """ process pipline """
        return process_chain(self.methods[methodname], obj, *args)
