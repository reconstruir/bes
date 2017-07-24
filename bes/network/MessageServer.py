#!/usr/bin/env python
#-*- coding:utf-8 -*-

from bes.common import json_util
from bes.thread import Waiter
from bes.system import log
from bes.net.util import Network
from bes.thread.decorators import synchronized_method

from TwistedReactorThread import TwistedReactorThread
import json, sys, threading

from twisted.internet.protocol import ServerFactory
from twisted.protocols.basic import LineReceiver
from twisted.internet import reactor, threads
 
class MessageServerFactory(ServerFactory):

  class MessageProcessor(object):
    def __init__(self, message, message_handler, transport):
      log.add_logging(self, 'message_processor')
      self.message = message
      self.message_handler = message_handler
      self.transport = transport
      
    def __deferred_process(self):
      response = self.message_handler(self.message)
      return response
 
    def deferred_process(self):
      d = threads.deferToThread(self.__deferred_process)
      d.addCallback(self.__callback)
      d.addErrback(self.__error_callback)
 
    def __callback(self, message):
      self.transport.send(message)
 
    def __error_callback(self, failure):
      self.log_e(failure.getErrorMessage())
      assert False, 'FIXME'
      self.write_callback('An error occured : %s%s' % (failure.getErrorMessage(), self._delimiter))

  class MessageProtocol(LineReceiver):

    delimiter = '\n'

    def __init__(self):
      log.add_logging(self, 'server_message_protocol')
  
    def connectionMade(self):
      self.client_ip = self.transport.getPeer().host
      self.log_i('Client connection from %s' % self.client_ip)
      if not self.factory.add_client(self):
        self.log_w('Too many connections')
        self.client_ip = None
        self.transport.loseConnection()
 
    def connectionLost(self, reason):
      self.log_i('Lost client connection.  reason=%s' % (reason))
      if self.client_ip:
        self.factory.remove_client(self)
 
    def lineReceived(self, line):
      message = json.loads(line)
      self.log_i('message recevied from %s: %s' % (self.client_ip, message))
      message_handler = self.factory._server.handle_message
      processor = MessageServerFactory.MessageProcessor(message, message_handler, self)
      processor.deferred_process()

    def send(self, message):
      line = json_util.to_json(message)
      self.log_i('server sending line "%s"' % (line))
      threads.deferToThread(self.sendLine, line)

  protocol = MessageProtocol
 
  def __init__(self, server):
    assert server, 'server needs to be valid.'
    log.add_logging(self, 'message_factory')
    self._server = server
    self._clients = []

  def add_client(self, client):
    self.log_i('add_client(%s)' % (client))
    num_clients = len(self._clients)
    max_num_clients = self._server._max_num_clients
    if num_clients  >= max_num_clients:
      self.log_w('Too many connections')
      return False
    self._clients.append(client)
    return True

  def remove_client(self, client):
    self.log_i('remove_client(%s)' % (client))
    assert client in self._clients
    self._clients.remove(client)

  def broadcast(self, message):
    for client in self._clients:
      client.send(message)

class MessageServer(TwistedReactorThread):

  def __init__(self, address, max_num_clients = 10):
    super(MessageServer, self).__init__(address)
    self.tag = 'twisted_message_server'
    self._max_num_clients = max_num_clients
    self._factory = None

  def bind(self):
    factory = MessageServerFactory(self)
    l = reactor.listenTCP(self._address[1], factory)
    host = l.getHost()
    self._address = ( host.host, host.port )
    self._factory = factory

  def handle_message(self, message):
    assert False, 'Not implemented'

  def send(self, message):
    assert False
    #self._transport.send(message)

  def broadcast(self, message):
    assert self._factory
    self._factory.broadcast(message)

if __name__ == '__main__':

  log.configure('debug')

  from MessageClient import MessageClient
  from MessageTest import make_message, get_line
  from bes.common import string_util 

  port = 0
  if len(sys.argv) > 1:
    port = int(sys.argv[1])
  print('MessageServer: Using port %d' % (port))



  class TestServer(MessageServer):
    def __init__(self, address):
      super(TestServer, self).__init__(address)
      self.tag = 'test_server'
    
    def handle_message(self, message):
      self.log_i('TestServer.handle_message(%s)' % (message))
      response = {
        'id': message['id'],
        'content': message['content'].upper(),
      }
      return response

  address = ( 'localhost', port)
  server = TestServer(address)
  server.start()

  print('Started server on %s' % (str(server._address)))

  clients = {}

  while True:
    line = get_line()
    if not line:
      continue

    cmd = line.lower()

    if cmd in [ 'exit', 'quit' ]:
      break
    elif cmd in [ 'client' ]:
      client_id = len(clients) + 1
      clients[client_id] = MessageClient(server._address)
      clients[client_id].connect()
      print 'New client with id %d connected.' % (client_id)
    elif cmd.startswith('message'):
      tokens = string_util.split_by_white_space(cmd)
      client_id = int(tokens[1])
      client = clients[client_id]
      content = ' '.join(tokens[2:])
      request = make_message(content)
      clients[client_id].send_and_wait(request)
      response = client.send_and_wait(request)
      print 'Got response "%s" for client %d' % (response, client_id)
    elif cmd.startswith('broadcast'):
      tokens = string_util.split_by_white_space(cmd)
      content = ' '.join(tokens[1:])
      message = make_message(content)
      server.broadcast(message)
    elif cmd in [ 'm', 'message' ]:
      assert False
#      message = {
#        'id': message_id,
#        'foo': 10,
#        'bar': 'hello',
#      }
#      print "sending message '%s'" % (message)
#      server.send(message)
#      message_id += 1
      continue

    continue

  server.stop()
  sys.exit(0)
