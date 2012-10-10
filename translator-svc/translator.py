#!/usr/bin/env python

from twisted.internet.protocol import Protocol
from twisted.internet.protocol import Factory
from twisted.internet.endpoints import TCP4ServerEndpoint
from twisted.internet import reactor

SVC_PORT = 8010

class TranslatorProtocol(Protocol):

    def __init__(self):
        self.read_buffer = ''

    def connectionMade(self):
        pass

    def connectionLost(self, reason):
        pass

    def dataReceived(self, data):
        # Append data to read buffer.
        self.read_buffer += data

        # Check for end-of-request marker.
        # (In out protocol a simple full-stop indicates end-of-request).
        if self.read_buffer.strip().endswith('.'):
            output_str = do_translation(self.read_buffer)
            print "In:  %s" % self.read_buffer
            print "Out: %s" % output_str
            self.read_buffer = ''
            self.transport.write(output_str)


def do_translation(input_str):
    return input_str.upper()

class TranslatorFactory(Factory):
    def buildProtocol(self, addr):
        return TranslatorProtocol()

print "Listening on localhost:8010"
endpoint = TCP4ServerEndpoint(reactor, SVC_PORT)
endpoint.listen(TranslatorFactory())
reactor.run()
