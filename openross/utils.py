import settings
import sys
import socket
import logging
import statsd
from twisted.internet import defer


def load_object(path):
    """ Load an object given its absolute object path, and return it
    """

    try:
        dot = path.rindex('.')
    except ValueError:
        raise ValueError("Error loading object '%s': not a full path" % path)

    module, name = path[:dot], path[dot + 1:]
    try:
        mod = __import__(module, {}, {}, [''])
    except ImportError, e:
        raise ImportError("Error loading object '%s' : %s" % (path, e))

    try:
        obj = getattr(mod, name)
    except AttributeError:
        raise NameError(
            "Module '%s' doesn't define any object named '%s'" % (module, name))

    return obj


def sentry_client():
    if settings.SENTRY_DSN:
        from raven import Client
        return Client(settings.SENTRY_DSN)


def capture_message(message, **kwargs):
    if settings.SENTRY_DSN:
        client = sentry_client()
        client.captureMessage(message, **kwargs)


def capture_warning(message, **kwargs):
    if settings.SENTRY_DSN:
        client = sentry_client()
        client.captureMessage(message, level=logging.WARNING, **kwargs)


def capture_exception(**kwargs):
    if settings.SENTRY_DSN:
        client = sentry_client()
        client.captureException(sys.exc_info(), **kwargs)


# Global to be used on all statsd keys for this instance
statsd_prefix = ''


def statsd_name():
    """ Determine a prefix to be applied to statsd name so that multiple instances on a
        single machine can be differentiated by statsd
    """
    global statsd_prefix
    if not statsd_prefix:
        args = sys.argv
        if '-p' in args:
            statsd_prefix = args[args.index('-p')+1]
        else:
            statsd_prefix = '0'
    return '%s.%s%s' % (settings.STATSD_NAME, socket.gethostname(), statsd_prefix)


def _generate_wrapped_deferred_decorator(contextmanager):
    """ This will generate a decorator that will wrap a deffered with a context manager.
        For example:

        class ToyContext:

            def __enter__(self):
                print 'Ping!'

            def __exit__(self, type, value, traceback):
                print 'Pong!'

         ping_pong = generate_wrapped_deffered_decorator(ToyContext)

         @pingpong
         def test:
            ...

        Will wrap the execution of test with 'Ping!' and 'Pong!'
    """
    def decorator_with_args(*contextargs):
        def decorator(func):
            @defer.inlineCallbacks
            def _inner(*a, **kw):
                r = None
                with contextmanager(*contextargs):
                    r = yield func(*a, **kw)
                defer.returnValue(r)
            return _inner
        return decorator
    return decorator_with_args


class StatsDTimingContext:
    """ Runs a statsd timer over a context manager """

    def __init__(self, application, label):
        self.application = application
        self.label = label
        self.t = statsd.Timer(self.application)

    def __enter__(self):
        self.t.start()

    def __exit__(self, type, value, traceback):
        self.t.stop(self.label)


# Decorator which times a deferred function
time_on_statsd = _generate_wrapped_deferred_decorator(StatsDTimingContext)
