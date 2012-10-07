#!/usr/bin/env python
from twisted.web import server, resource
from twisted.internet import reactor

class HelloResource(resource.Resource):
    isLeaf = True

    def render_GET(self, request):
        return "Hello World"

reactor.listenTCP(8080, server.Site(HelloResource()))
reactor.run()
