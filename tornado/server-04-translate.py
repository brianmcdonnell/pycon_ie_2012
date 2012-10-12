#!/usr/bin/env python
import tornado.ioloop
import tornado.web

from utils import validate_params

PORT = 8080

class MainHandler(tornado.web.RequestHandler):

    @tornado.web.asynchronous
    def get(self):
        if not validate_params(self, ('data',)): return

        def translation_callback(response):
            if t.error:
                self.set_status(500)
                self.write("Internal Server Error. %s" % t.error)
            else:
                self.write(response)
            self.finish()

        # Connect to translator service
        from tortranslator import TorTranslator
        t = TorTranslator('localhost', 8010)
        t.translate(self.get_argument('data'), translation_callback)


application = tornado.web.Application([
    (r"/translate/", MainHandler),
])

if __name__ == "__main__":
    application.listen(PORT)
    print "Listening on http://localhost:%s/translate/ params:data" % PORT
    tornado.ioloop.IOLoop.instance().start()
