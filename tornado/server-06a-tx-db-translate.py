#!/usr/bin/env python
import tornado.ioloop
import tornado.web
import tornado.gen
import asyncmongo

import tornado.platform.twisted
tornado.platform.twisted.install()
from twisted.internet import reactor

from utils import validate_params

MONGO_HOST = 'localhost'
MONGO_PORT = 27017
MONGO_DB = 'pycon'

SVC_HOST = 'localhost'
SVC_PORT = 8010

PORT = 8080

class MainHandler(tornado.web.RequestHandler):

    def __init__(self, *args, **kwargs):
        super(MainHandler, self).__init__(*args, **kwargs)
        self.db = asyncmongo.Client(dbname=MONGO_DB, host=MONGO_HOST, port=MONGO_PORT, pool_id='pycon')

    @tornado.web.asynchronous
    @tornado.gen.engine
    def get(self):
        if not validate_params(self, ('data','user')): return

        # Check we have the specified user in the database
        (res, err_dict) = yield tornado.gen.Task(self.db.users.find_one, {'name': self.get_argument('user')})
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

        # TWISTED WITHIN TORNADO

        def translate_callback(result):
            self.write(str(result))
            self.finish()
        def translate_errback(result):
            self.set_status(500)
            self.write(str(result))
            self.finish()
        # Connect to translator service using twisted :-)
        from txtranslator import TranslatorClient
        client = TranslatorClient(SVC_HOST, SVC_PORT)
        d = client.translate2(str(self.get_argument('data')))
        d.addCallback(translate_callback)
        d.addErrback(translate_errback)

application = tornado.web.Application([
    (r"/translate/", MainHandler),
])

# Ctrl-C was hanging to process after adding the twisted reactor
import signal
import sys
def signal_handler(signal, frame):
        print 'You pressed Ctrl+C'
        # As per here:
        # http://www.tornadoweb.org/documentation/twisted.html
        reactor.fireSystemEvent('shutdown')
        reactor.disconnectAll()
        sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)
print 'Press Ctrl+C to exit'

if __name__ == "__main__":
    application.listen(PORT)
    print "Listening on http://localhost:%s/translate/ params:name,user" % PORT
    tornado.ioloop.IOLoop.instance().start()
