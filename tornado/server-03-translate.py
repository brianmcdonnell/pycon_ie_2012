#!/usr/bin/env python
import socket

import tornado.iostream
import tornado.ioloop
import tornado.web

class MainHandler(tornado.web.RequestHandler):

    @tornado.web.asynchronous
    def get(self):
        # ENSURE URL PARAMS WERE PASSED
        data = self.get_argument('data', None)
        if data is None:
            self.set_status(400)
            self.write("Bad Request. No data to translate\n")
            self.finish()

        def send_translation_data():
            stream.write(str(data))
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
    application.listen(8080)
    tornado.ioloop.IOLoop.instance().start()
