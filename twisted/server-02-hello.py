#!/usr/bin/env python
from twisted.web import server, resource
from twisted.internet import reactor
from twisted.web.server import NOT_DONE_YET

def delayed_render(request, name):
    request.write("Hello %s, sorry about the delay." % name)
    request.finish()

class HelloResource(resource.Resource):
    isLeaf = True

    def render_GET(self, request):
        # ENSURE GET PARAMS WERE PASSED
        name = request.args.get('name', None)
        if name is None:
            return resource.ErrorPage(400, "Bad Request", "Missing 'name' param.").render(request)
        name = name[0]

        # Render in a delayed callback
        delay_seconds = 2
        print "Delaying for %s seconds." % delay_seconds
        reactor.callLater(delay_seconds, delayed_render, request, name)
        return NOT_DONE_YET

reactor.listenTCP(8080, server.Site(HelloResource()))
reactor.run()
