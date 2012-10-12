#!/usr/bin/env python
import socket

import tornado.iostream
import tornado.ioloop
import tornado.web

from utils import validate_params

PORT = 8080

class MainHandler(tornado.web.RequestHandler):

    @tornado.web.asynchronous
    def get(self):
        if not validate_params(self, ('name',)): return

        def send_translation_data():
            stream.write(str(self.get_argument('name')))
            stream.read_until('.', translation_complete)

        def translation_complete(translated_data):
            self.write(translated_data)
            self.finish()

        # Connect to translator service
        # Just like in Twisted I have to implement TranslationProtocol manually.
        # Tornado gives me an async iostream class, but nothing more.
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        stream = tornado.iostream.IOStream(s)
        stream.connect(("localhost", 8010), send_translation_data)


application = tornado.web.Application([
    (r"/translate/", MainHandler),
])

if __name__ == "__main__":
    application.listen(PORT)
    print "Listening on http://localhost:%s/translate/ params:data" % PORT
    tornado.ioloop.IOLoop.instance().start()
