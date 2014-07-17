# -*- coding: utf-8 -*-

from twisted.internet import protocol, reactor

class Echo(protocol.Protocol):
    def dataReceived(self, data):
        for d in data:
            self.transport.write(d)

class EchoFactory(protocol.Factory):
    def buildProtocol(self, addr):
        return Echo()

reactor.listenTCP(1234, EchoFactory())
reactor.run()