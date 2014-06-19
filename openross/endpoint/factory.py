from twisted.web import server
from endpoint import BobRossEndpoint


def get_factory():
    """ Build site from twisted endpoint """

    root = BobRossEndpoint()
    return server.Site(root)
