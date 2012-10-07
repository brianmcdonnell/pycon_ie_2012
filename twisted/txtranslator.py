from twisted.internet.protocol import Protocol, ClientFactory
from twisted.internet import defer

class TranslatorClientProtocol(Protocol):

    def __init__(self, *args, **kw):
        self.read_buffer = ''

    def connectionMade(self):
        print "Connection made. Sending: %s" % self.factory.input_str
        self.transport.write(self.factory.input_str)

    def dataReceived(self, data):
        print "Data received: %s" % data
        self.read_buffer += data
        if self.read_buffer.strip().endswith('.'):
            self.factory.deferred.callback(data)

class TranslatorClientFactory(ClientFactory):

    def __init__(self):
        self.deferred = defer.Deferred()

    def set_callback(self, f, *args, **kwargs):
        ''' Wrapper to hide deferred for server-03 '''
        self.deferred.addCallback(f, *args, **kwargs)

    def buildProtocol(self, addr):
        print 'Connected.'
        proto = TranslatorClientProtocol()
        proto.factory = self
        return proto

    def clientConnectionFailed(self, connector, reason):
        ''' Called if the server connection failed to connect.
        '''
        self.deferred.errback(reason)


class TranslatorClient():

    def __init__(self, host, port):
        self.host = host
        self.port = port

    def translate1(self, input_str, callback, *args, **kwargs):
        factory = TranslatorClientFactory()
        factory.input_str = input_str
        factory.deferred.addCallback(callback, *args, **kwargs)
        from twisted.internet import reactor
        reactor.connectTCP(self.host, self.port, factory)

    def translate2(self, input_str):
        factory = TranslatorClientFactory()
        factory.input_str = input_str

        from twisted.internet import reactor
        reactor.connectTCP(self.host, self.port, factory)
        return factory.deferred
