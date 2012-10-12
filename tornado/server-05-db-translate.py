#!/usr/bin/env python
import tornado.ioloop
import tornado.web
import asyncmongo

from utils import validate_params

MONGO_HOST = 'localhost'
MONGO_PORT = 27017
MONGO_DB = 'pycon'

PORT = 8080

class MainHandler(tornado.web.RequestHandler):

    @property
    def db(self):
        if not hasattr(self, '_db'):
            self._db = asyncmongo.Client(dbname=MONGO_DB, host=MONGO_HOST, port=MONGO_PORT, 
                                            maxcached=10, maxconnections=50, pool_id='mypool')
        return self._db

    @tornado.web.asynchronous
    def get(self):
        if not validate_params(self, ('data','user')): return

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
                trans.translate(self.get_argument('data'), functools.partial(translation_callback, trans))

        self.db.users.find_one({'name': self.get_argument('user')}, callback=getuser_callback)

application = tornado.web.Application([
    (r"/translate/", MainHandler),
])

if __name__ == "__main__":
    application.listen(PORT)
    print "Listening on http://localhost:%s/translate/ params:name,user" % PORT
    tornado.ioloop.IOLoop.instance().start()
