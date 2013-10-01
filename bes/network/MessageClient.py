#!/usr/bin/env python
#-*- coding:utf-8 -*-

from twisted.internet.protocol import ReconnectingClientFactory
from twisted.internet.protocol import Protocol, ClientFactory
from twisted.protocols.basic import LineReceiver
from twisted.internet import reactor, threads

from TwistedReactorThread import TwistedReactorThread

from twisted.internet import reactor, defer

from Queue import Queue, Empty as QueueEmptyException

from bes.common.Decorator import synchronized_method

from bes.common import Log, Waiter

import json, sys, pprint, threading

class MessageProtocol(LineReceiver):

  delimiter = '\n'

  def __init__(self, client):
    Log.add_logging(self, 'client_message_protocol')
    self._client = client
    self._id = 1

  def lineReceived(self, line):
    message = json.loads(line)

    if Log.get_tag_level(self.tag) == Log.DEBUG:
      formatted_message = pprint.pformat(message)
      self.log_d('Client got message:')
      for line in formatted_message.split('\n'):
        self.log_i(line)
    else:
      self.log_i('Client got message: "%s"' % (message))
      
    self._client._transport_received_message(message)

  def connectionMade(self):
    self._client._transport_connected()

  def send(self, message):
    line = json.dumps(message)
    self.log_i('client sending line "%s"' % (line))
    threads.deferToThread(self.sendLine, line)

class MessageProtocolClientFactory(ReconnectingClientFactory):

  def __init__(self, client):
    Log.add_logging(self, 'message_protocol_client_factory')
    self._client = client

  def startedConnecting(self, connector):
    self.log_i('Started to connect.')
    ReconnectingClientFactory.startedConnecting(self, connector)

  def buildProtocol(self, addr):
    self.log_i('Factory connected to %s' % (str(addr)))
    transport =  MessageProtocol(self._client)
    self._client._set_transport(transport)
    return transport

  def clientConnectionLost(self, connector, reason):
    self.log_i('Connection lost.  reason=%s' % (reason))
    ReconnectingClientFactory.clientConnectionLost(self, connector, reason)

  def clientConnectionFailed(self, connector, reason):
    self.log_i('Connection failed.  reason=%s' % (reason))
    ReconnectingClientFactory.clientConnectionFailed(self, connector, reason)

class MessageClient(TwistedReactorThread):

  def __init__(self, address, message_handler = None):
    super(MessageClient, self).__init__(address)
    self.tag = 'message_client'
    self._transport = None
    self._queue = Queue()
    self._message_handler = message_handler

  def bind(self):
    reactor.connectTCP(self._address[0], self._address[1], MessageProtocolClientFactory(self))

  def connect(self, timeout = 1.0):
    self._connected_waiter = Waiter()
    self.start()
    return self._connected_waiter.wait(timeout = timeout)
#      raise RuntimeError('Failed to connect')

  def _transport_received_message(self, message):
    if self._message_handler:
      handled = self._message_handler(message)
      if handled:
        return
    self._queue.put(message, block = True, timeout = 1.0)

  def _transport_connected(self):
    self._connected_waiter.notify()

  @synchronized_method('_lock')
  def send(self, message):
    assert self._transport
    self._transport.send(message)

  @synchronized_method('_lock')
  def _set_transport(self, transport):
    assert transport
    self._transport = transport

  def send_and_wait(self, message, timeout = None):
    self.send(message)
    response = self._queue.get(block = True, timeout = timeout)
    self._queue.task_done()
    return response

if __name__ == '__main__':
  from bes.common import StringUtil 
  from MessageTest import make_message, get_line

  Log.set_level(Log.INFO)

  host = 'localhost'
  if len(sys.argv) > 1:
    host = sys.argv[1]

  port = 9999
  if len(sys.argv) > 2:
    port = int(sys.argv[2])

  address = ( host, port )
  print('MessageClient: Using address %s' % (str(address)))

  client = MessageClient(address)
  client.connect()

  print('Type exit to stop server; message <content> to send message...')
  while True:
    line = get_line()
    if not line:
      continue
    
    cmd = line.lower()

    if cmd in [ 'exit', 'quit' ]:
      break

    if cmd.startswith('message'):
      tokens = StringUtil.split_by_white_space(cmd)
      content = ' '.join(tokens[1:])
      message = make_message(content)
      print "sending message '%s'" % (message)
      response = client.send_and_wait(message, timeout = 5.0)
      print "   got response '%s'" % (response)
      continue
    
    continue

  client.stop()
  sys.exit(0)
