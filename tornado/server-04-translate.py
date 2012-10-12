#!/usr/bin/env python
import tornado.ioloop
import tornado.web

PORT = 8080

class MainHandler(tornado.web.RequestHandler):

    @tornado.web.asynchronous
    def get(self):
        # ENSURE URL PARAMS WERE PASSED
        data = self.get_argument('data', None)
        if data is None:
            self.set_status(400)
            self.write("Bad Request. No data to translate.")
            self.finish()
        if not data.strip().endswith('.'):
            self.write("Bad Request. Input data must end with period.")
            self.finish()

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
        t.translate(data, translation_callback)


application = tornado.web.Application([
    (r"/translate/", MainHandler),
])

if __name__ == "__main__":
    application.listen(PORT)
    print "Listening on http://localhost:%s/translate/ params:data" % PORT
    tornado.ioloop.IOLoop.instance().start()
