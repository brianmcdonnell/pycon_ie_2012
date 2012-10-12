#!/usr/bin/env python
import datetime

import tornado.ioloop
import tornado.web

from utils import validate_params

PORT = 8080

class MainHandler(tornado.web.RequestHandler):

    @tornado.web.asynchronous
    def get(self):
        if not validate_params(self, ('name',)): return

        def render_async():
            self.write("Hello world, %s (delayed)" % self.get_argument('name'))
            self.finish()

        delay = datetime.timedelta(days=0, seconds=2)
        # Can't pass args to callback for some reason. 
        # Could have used a instance vars & method, but
        # using closure instead.
        tornado.ioloop.IOLoop.instance().add_timeout(delay, render_async)


application = tornado.web.Application([
    (r"/translate/", MainHandler),
])

if __name__ == "__main__":
    application.listen(PORT)
    print "Listening on http://localhost:%s/translate/ params:name" % PORT
    tornado.ioloop.IOLoop.instance().start()
