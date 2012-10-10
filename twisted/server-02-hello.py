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
        # Check that the 'name' URL param was passed.
        name = request.args.get('name', None)
        if name is None:
            return resource.ErrorPage(400, "Bad Request", "Missing 'name' param.").render(request)
        name = name[0]

        delay_seconds = 2
        print "Delaying for %s seconds." % delay_seconds
        # Delay requires a callback
        reactor.callLater(delay_seconds, delayed_render, request, name)
        return NOT_DONE_YET

reactor.listenTCP(8080, server.Site(HelloResource()))
reactor.run()
