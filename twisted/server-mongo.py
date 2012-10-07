#!/usr/bin/env python
from twisted.web import server, resource
from twisted.internet import defer, reactor
from twisted.web.server import NOT_DONE_YET

import txmongo

@defer.inlineCallbacks
def find_user(request):
    mongo = yield txmongo.MongoConnection()
    pycondb = mongo.pycon
    users = pycondb.users

    # fetch some documents
    user = yield users.find({'name': 'brian'})
    #user = yield users.find()
    print user
    request.write('done')
    request.finish()


def cb_cxn_est(result_cxn, request, *args, **kwargs):
    #print "cxn est %s %s" % (result_cxn, request)
    users = result_cxn.pycon.users
    query_defer = users.find({'name':'brian'})
    query_defer.addCallback(cb_get_user, request)
    query_defer.addErrback(errback_query, request)

def errback_cxn(result, request, *args, **kwargs):
    print "ERROR cxn"
    print result
    request.write('Error 500')
    request.finish()

def cb_get_user(result, request, *args, **kwargs):
    print "print_user %s" % result
    #import pdb;pdb.set_trace()

    input_str = request.args['data'][0]
    output_str = input_str.upper()
    request.setHeader("content-type", "text/html")
    request.write("<html>\
<head><title>Translator</title></head>\
<body style=\"font-size: xx-large\">\
%s\
</body>\
</html>" % output_str)
    request.finish()

def errback_query(result, request, *args, **kwargs):
    print "ERROR query"
    print result
    request.write('Error 500')
    request.finish()


class TranslatorResource(resource.Resource):
    isLeaf = True

    def render_GET(self, request):
        if not 'data' in request.args:
            return "Bad request"

        mongo_defer = txmongo.MongoConnection()
        mongo_defer.addCallback(cb_cxn_est, request)
        mongo_defer.addErrback(errback_cxn, request)

        return NOT_DONE_YET

reactor.listenTCP(8080, server.Site(TranslatorResource()))
reactor.run()
