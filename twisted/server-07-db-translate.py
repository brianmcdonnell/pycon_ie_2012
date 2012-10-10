#!/usr/bin/env python
from twisted.web import server, resource
from twisted.internet import defer, reactor
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

        self.handle_request(request)

        return NOT_DONE_YET

    @defer.inlineCallbacks
    def handle_request(self, request):
        try:
            username = request.args['user'][0]
            # Pull the specified user from the database
            cxn = yield txmongo.MongoConnection()
            user = yield cxn.pycon.users.find_one({'name': username})
            if user is None:
                request.write("<html><head><title>Translator</title></head>\
                                <body style=\"font-size: xx-large\">\
                                <h3>Insufficient Funds</h3></body>\
                                </html>")
            else:
                # Call the translator service
                input_str = request.args['data'][0]
                from txtranslator import TranslatorClient
                client = TranslatorClient(SVC_HOST, SVC_PORT)
                output_str = yield client.translate2(input_str)

                # Write the response
                request.write("<html><head><title>Translator</title></head><body>\
                <h3>User: %s ($%s)</h3>\
                <div>Input: %s</div>\
                <div>Output: %s</div>\
                </body></html>" % (str(user['name']), user['balance'], input_str, output_str))
        except Exception, err:
            request.write(resource.ErrorPage(500, "Internal Server Error.", err).render(request))
        finally:
            request.finish()

root = resource.Resource()
root.putChild("translate", TranslatorResource())
site = server.Site(root)
reactor.listenTCP(8080, site)
reactor.run()
