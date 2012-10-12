#!/usr/bin/env python
from twisted.web import server, resource
from twisted.internet import defer, reactor
from twisted.web.server import NOT_DONE_YET

from utils import validate_params
import txmongo

SVC_HOST = 'localhost'
SVC_PORT = 8010

PORT = 8080

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
            cxn = yield txmongo.MongoConnection()
            # Don't yield the user query
            user_defer = cxn.pycon.users.find_one({'name': username})

            # Go ahead with the translation regardless of 
            # whether we find a user.
            input_str = request.args['data'][0]
            from txtranslator import TranslatorClient
            client = TranslatorClient(SVC_HOST, SVC_PORT)
            output_defer = client.translate2(input_str)

            # Wait until we have both results.
            output_str = yield output_defer
            user = yield user_defer

            if user:
                request.write("%s: %s" % (str(user['name']), output_str))
            else:
                request.write("User '%s' not found!" % username)
        except Exception, err:
            print err
            request.write(resource.ErrorPage(500, "Internal Server Error.", err).render(request))
        finally:
            request.finish()

root = resource.Resource()
root.putChild("translate", TranslatorResource())
site = server.Site(root)
reactor.listenTCP(PORT, site)
reactor.run()

print "Listening on http://localhost:%s/translate/ params:data,user" % PORT
