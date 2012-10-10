#!/usr/bin/env python
from twisted.web import server, resource
from twisted.internet import reactor
from twisted.web.server import NOT_DONE_YET

from utils import validate_params
import txmongo

SVC_HOST = 'localhost'
SVC_PORT = 8010

class TranslatorResource(resource.Resource):
    isLeaf = True

    def render_GET(self, request):
        error_str = validate_params(request, ('user', 'data'))
        if error_str: return error_str

        mongo_defer = txmongo.MongoConnection()
        mongo_defer.addCallback(mongocxn_callback, request)
        mongo_defer.addErrback(mongocxn_errback, request)

        return NOT_DONE_YET

def mongocxn_callback(cxn, request, *args, **kwargs):
    username = request.args['user'][0]
    query_defer = cxn.pycon.users.find_one({'name': username})
    query_defer.addCallback(getuser_callback, request)
    query_defer.addErrback(getuser_errback, request)

def mongocxn_errback(err, request, *args, **kwargs):
    request.write(resource.ErrorPage(500, "Failed to get DB Connection", err).render(request))
    request.finish()

def getuser_callback(user, request, *args, **kwargs):
    if user is None or user.get('balance', 0.0) <= 0.0:
        # Refuse to do the translation
        request.setHeader("content-type", "text/html")
        request.write("<html><head><title>Translator</title></head>\
                                <body style=\"font-size: xx-large\">\
                                <h3>Insufficient Funds</h3></body>\
                        </html>")
        request.finish()
    else:
        # Call the translator service
        input_str = request.args['data'][0]
        from txtranslator import TranslatorClient
        client = TranslatorClient(SVC_HOST, SVC_PORT)
        d = client.translate2(input_str)
        d.addCallback(translator_callback, request, user)
        d.addErrback(translator_errback, request, user)

def getuser_errback(err, request, *args, **kwargs):
    request.write(resource.ErrorPage(500, "Error retrieving user data.", err).render(request))
    request.finish()

def translator_callback(output_str, request, user):

    input_str = request.args['data'][0]
    request.setHeader("content-type", "text/html")
    request.write("<html>\
<head><title>Translator</title></head>\
<body style=\"font-size: xx-large\">\
<h3>User: %s ($%s)</h3>\
<div>Input: %s</div>\
<div>Output: %s</div>\
</body>\
</html>" % (str(user['name']), user['balance'], input_str, output_str))
    request.finish()

def translator_errback(err, request, user):
    request.write(resource.ErrorPage(500, "Error calling translator service.", err).render(request))
    request.finish()

root = resource.Resource()
root.putChild("translate", TranslatorResource())
site = server.Site(root)
reactor.listenTCP(8080, site)
reactor.run()
