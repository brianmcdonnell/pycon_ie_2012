#!/usr/bin/env python
from twisted.web import server, resource
from twisted.internet import reactor

PORT = 8080

class HelloResource(resource.Resource):
    isLeaf = True

    def render_GET(self, request):
        return "Hello World"

reactor.listenTCP(PORT, server.Site(HelloResource()))
print "Listening on http://localhost:%s" % PORT
reactor.run()
