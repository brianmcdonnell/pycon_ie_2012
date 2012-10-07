#!/usr/bin/env python
from twisted.web import server, resource
from twisted.internet import defer, reactor
from twisted.web.server import NOT_DONE_YET

import txmongo

SVC_HOST = 'localhost'
SVC_PORT = 8010

@defer.inlineCallbacks
def handle_request(request):
    try:
        # Get a mongo db connection
        cxn = yield txmongo.MongoConnection()

        # Pull the specified user from the database
        username = request.args['user'][0]
        user_defer = cxn.pycon.users.find_one({'name': username})

        # Call the translator service
        input_str = request.args['data'][0]
        from txtranslator import TranslatorClient
        client = TranslatorClient(SVC_HOST, SVC_PORT)
        output_str_defer = client.translate2(input_str)

        # Allows both calls to run concurrently
        user = yield user_defer
        output_str = yield output_str_defer

        # Write the response
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
    except Exception, err:
        request.write(resource.ErrorPage(500, "Error retrieving user data.", err).render(request))
        request.finish()

class TranslatorResource(resource.Resource):
    isLeaf = True

    def render_GET(self, request):
        user = request.args.get('user', None)
        if user is None:
            return resource.ErrorPage(400, "Bad Request", "Missing 'user' url parameter.").render(request)
        data = request.args.get('data', None)
        if data is None:
            return resource.ErrorPage(400, "Bad Request", "Missing 'data' url parameter. Nothing to translate.").render(request)
        input_str = data[0]
        if not input_str.strip().endswith('.'):
            return resource.ErrorPage(400, "Bad Request", "Input data must end with period").render(request)

        handle_request(request)

        return NOT_DONE_YET

root = resource.Resource()
root.putChild("translate", TranslatorResource())
site = server.Site(root)
reactor.listenTCP(8080, site)
reactor.run()
