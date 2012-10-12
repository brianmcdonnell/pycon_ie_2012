#!/usr/bin/env python
from twisted.web import server, resource
from twisted.internet import reactor
from twisted.web.server import NOT_DONE_YET

from utils import validate_params

SVC_HOST = 'localhost'
SVC_PORT = 8010

PORT = 8080

class TranslatorResource(resource.Resource):
    isLeaf = True

    def render_GET(self, request):
        # Ensure URL params were passed
        error_str = validate_params(request, ('data',))
        if error_str: return error_str

        from txtranslator import TranslatorClient
        client = TranslatorClient(SVC_HOST, SVC_PORT)
        # Pass callback function only (Not doing any error handling)
        client.translate1(request.args['data'][0], translator_callback, request)

        return NOT_DONE_YET

def translator_callback(result, request):
    request.write(result)
    request.finish()

root = resource.Resource()
root.putChild("translate", TranslatorResource())
site = server.Site(root)
reactor.listenTCP(PORT, site)
reactor.run()

print "Listening on http://localhost:%s/translate/ params:data" % PORT
