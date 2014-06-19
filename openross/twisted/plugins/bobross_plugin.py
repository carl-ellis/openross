from zope.interface import implements
from twisted.internet import reactor
from twisted.python import usage
from twisted.plugin import IPlugin
from twisted.application.service import IServiceMaker
from twisted.application import internet
import settings
from endpoint import factory


class Options(usage.Options):
    """ Command line options for the plugin """
    optParameters = [['port', 'p', 5500, 'The port number to listen on.']]


class BobRossMaker(object):
    implements(IServiceMaker, IPlugin)
    tapname = 'openross'
    description = 'Open BobRoss Image Processing Service'
    options = Options

    def makeService(self, options):
        """
        Construct a TCPServer from a factory defined in bobross
        """
        return internet.TCPServer(int(options['port']), factory.get_factory())


reactor.suggestThreadPoolSize(settings.THREAD_POOL_SIZE)
serviceMaker = BobRossMaker()
