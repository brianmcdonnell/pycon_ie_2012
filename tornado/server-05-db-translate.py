#!/usr/bin/env python
import tornado.ioloop
import tornado.web
import asyncmongo

MONGO_HOST = 'localhost'
MONGO_PORT = 27017
MONGO_DB = 'pycon'

class MainHandler(tornado.web.RequestHandler):

    @property
    def db(self):
        if not hasattr(self, '_db'):
            self._db = asyncmongo.Client(dbname=MONGO_DB, host=MONGO_HOST, port=MONGO_PORT, 
                                            maxcached=10, maxconnections=50, pool_id='mypool')
        return self._db

    @tornado.web.asynchronous
    def get(self):
        # ENSURE URL PARAMS WERE PASSED
        username = self.get_argument('user', None)
        if username is None:
            self.set_status(400)
            self.write("Bad Request. Missing 'user' url parameter.")
            self.finish()
            return
        data = self.get_argument('data', None)
        if data is None:
            self.set_status(400)
            self.write("Bad Request. No data to translate.")
            self.finish()
            return
        if not data.strip().endswith('.'):
            self.set_status(400)
            self.write("Bad Request. Input data must end with period.")
            self.finish()
            return

        def translation_callback(translator, output_str):
            if translator.error:
                self.set_status(500)
                self.write("Internal Server Error. %s" % translator.error)
            else:
                self.write(output_str)
            self.finish()

        def getuser_callback(user, error):
            if error:
                self.set_status(500)
                self.write("Internal Server Error. %s" % error)
                self.finish()
            elif not user:
                self.set_status(403)
                self.write("Forbidden.")
                self.finish()
            else:
                # Connect to translator service
                from tortranslator import TorTranslator
                trans = TorTranslator('localhost', 8010)
                import functools
                trans.translate(data, functools.partial(translation_callback, trans))

        self.db.users.find_one({'name': username}, callback=getuser_callback)

application = tornado.web.Application([
    (r"/translate/", MainHandler),
])

if __name__ == "__main__":
    application.listen(8080)
    tornado.ioloop.IOLoop.instance().start()
