#!/usr/bin/env python
import tornado.ioloop
import tornado.web
import tornado.gen
import asyncmongo

from utils import validate_params

MONGO_HOST = 'localhost'
MONGO_PORT = 27017
MONGO_DB = 'pycon'

PORT = 8080

class MainHandler(tornado.web.RequestHandler):

    def __init__(self, *args, **kwargs):
        super(MainHandler, self).__init__(*args, **kwargs)
        self.db = asyncmongo.Client(dbname=MONGO_DB, host=MONGO_HOST, port=MONGO_PORT, pool_id='pycon')

    @tornado.web.asynchronous
    @tornado.gen.engine
    def get(self):
        if not validate_params(self, ('data',)): return

        # Check we have the specified user in the database
        self.db.users.find_one({'name': self.get_argument('user')}, 
                callback=(yield tornado.gen.Callback("db_key")))
        # Connect to translator service
        from tortranslator import TorTranslator
        translator = TorTranslator('localhost', 8010)
        translator.translate(self.get_argument('data'), callback=(yield tornado.gen.Callback('translator_key')))

        # NOTE: BOTH THE DB QUERY AND THE TRANSLATION HAVE ALREADY STARTED
        (db_res, db_err_dict) = yield tornado.gen.Wait("db_key")
        output_str = yield tornado.gen.Wait("translator_key")

        # Deal with db results
        db_error = db_err_dict.get('error', None)
        if db_error:
            self.set_status(500)
            self.write("Internal Server Error. %s" % db_error)
            self.finish()
            return
        user = db_res[0] if len(db_res) > 0 else None
        if not user:
            self.set_status(403)
            self.write("Forbidden.")
            self.finish()
            return

        # Deal with translator results
        if translator.error:
            self.set_status(500)
            self.write("Internal Server Error. %s" % translator.error)
            self.finish()
        else:
            self.write(output_str)
            self.finish()

application = tornado.web.Application([
    (r"/translate/", MainHandler),
])

if __name__ == "__main__":
    application.listen(PORT)
    print "Listening on http://localhost:%s/translate/ params:name,user" % PORT
    tornado.ioloop.IOLoop.instance().start()
