#!/usr/bin/env python
import tornado.ioloop
import tornado.web
import tornado.gen
import asyncmongo

MONGO_HOST = 'localhost'
MONGO_PORT = 27017
MONGO_DB = 'pycon'

class MainHandler(tornado.web.RequestHandler):

    def __init__(self, *args, **kwargs):
        super(MainHandler, self).__init__(*args, **kwargs)
        self.db = asyncmongo.Client(dbname=MONGO_DB, host=MONGO_HOST, port=MONGO_PORT, pool_id='pycon')

    @tornado.web.asynchronous
    @tornado.gen.engine
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

        # Check we have the specified user in the database
        (res, err_dict) = yield tornado.gen.Task(self.db.users.find_one, {'name': username})
        error = err_dict.get('error', None)
        if error:
            self.set_status(500)
            self.write("Internal Server Error. %s" % error)
            self.finish()
            return
        user = res[0] if len(res) > 0 else None
        if not user:
            self.set_status(403)
            self.write("Forbidden.")
            self.finish()
            return

        # Connect to translator service
        from tortranslator import TorTranslator
        translator = TorTranslator('localhost', 8010)
        output_str = yield tornado.gen.Task(translator.translate, data)
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
    application.listen(8080)
    tornado.ioloop.IOLoop.instance().start()
