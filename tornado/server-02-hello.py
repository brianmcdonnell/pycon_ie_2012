#!/usr/bin/env python
import datetime

import tornado.ioloop
import tornado.web


class MainHandler(tornado.web.RequestHandler):

    @tornado.web.asynchronous
    def get(self):
        # ENSURE URL PARAMS WERE PASSED
        name = self.get_argument('name', None)

        def render_async():
            self.write("Hello world, %s (delayed)" % name)
            self.finish()

        delay = datetime.timedelta(days=0, seconds=2)
        # Can't pass args to callback for some reason. 
        # Could have used a instance vars & method, but
        # using closure instead.
        tornado.ioloop.IOLoop.instance().add_timeout(delay, render_async)


application = tornado.web.Application([
    (r"/", MainHandler),
])

if __name__ == "__main__":
    application.listen(8080)
    tornado.ioloop.IOLoop.instance().start()
