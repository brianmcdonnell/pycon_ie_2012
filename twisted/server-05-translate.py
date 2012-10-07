#!/usr/bin/env python
from twisted.web import server, resource
from twisted.internet import reactor
from twisted.web.server import NOT_DONE_YET

SVC_HOST = 'localhost'
SVC_PORT = 8010

def translator_callback(result, request):
    request.write(result)
    request.finish()

def translator_errback(result, request):
    request.write(resource.ErrorPage(500, "Translator Failed", result).render(request))
    request.finish()

class TranslatorResource(resource.Resource):
    isLeaf = True

    def render_GET(self, request):
        # ENSURE GET PARAMS WERE PASSED
        data = request.args.get('data', None)
        if data is None:
            return resource.ErrorPage(400, "Bad Request", "Missing 'data' url parameter. Nothing to translate.").render(request)
        input_str = data[0]
        if not input_str.strip().endswith('.'):
            return resource.ErrorPage(400, "Bad Request", "Input data must end with period").render(request)

        from txtranslator import TranslatorClient
        client = TranslatorClient(SVC_HOST, SVC_PORT)
        d = client.translate2(input_str)
        d.addCallback(translator_callback, request)
        d.addErrback(translator_errback, request)

        return NOT_DONE_YET

root = resource.Resource()
root.putChild("translate", TranslatorResource())
site = server.Site(root)
reactor.listenTCP(8080, site)
reactor.run()
