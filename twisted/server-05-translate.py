#!/usr/bin/env python
from twisted.web import server, resource
from twisted.internet import reactor
from twisted.web.server import NOT_DONE_YET

from utils import validate_params

SVC_HOST = 'localhost'
SVC_PORT = 8010

class TranslatorResource(resource.Resource):
    isLeaf = True

    def render_GET(self, request):
        error_str = validate_params(request, ('data',))
        if error_str: return error_str

        from txtranslator import TranslatorClient
        client = TranslatorClient(SVC_HOST, SVC_PORT)
        # Use a deferred to handle callback & errback
        d = client.translate2(request.args['data'][0])
        d.addCallback(translator_callback, request)
        d.addErrback(translator_errback, request)

        return NOT_DONE_YET

def translator_callback(result, request):
    request.write(result)
    request.finish()

def translator_errback(result, request):
    request.write(resource.ErrorPage(500, "Translator Failed", result).render(request))
    request.finish()

root = resource.Resource()
root.putChild("translate", TranslatorResource())
site = server.Site(root)
reactor.listenTCP(8080, site)
reactor.run()
