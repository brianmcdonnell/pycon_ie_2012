#!/usr/bin/env python
import tornado.ioloop
import tornado.web

PORT = 8080

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Hello world")

application = tornado.web.Application([
    (r"/", MainHandler),
])

if __name__ == "__main__":
    application.listen(PORT)
    print "Listening on http://localhost:%s" % PORT
    tornado.ioloop.IOLoop.instance().start()
