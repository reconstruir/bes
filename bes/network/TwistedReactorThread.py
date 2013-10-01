#!/usr/bin/env python
#-*- coding:utf-8 -*-

from bes.common import Log, Waiter
from bes.common.Decorator import synchronized_method
import threading
from twisted.internet import reactor
from twisted.internet.error import ReactorAlreadyRunning
 
class TwistedReactorThread(object):

  def __init__(self, address):
    Log.add_logging(self, 'reactor_thread')
    self._address = address
    self._thread = None
    self._lock = threading.Lock()

  @synchronized_method('_lock')
  def start(self):
    assert not self._thread
    self._thread = threading.Thread(target = self.__thread_main)
    self._thread.setDaemon(True) # don't hang on exit
    self._waiter = Waiter()
    self._thread.start()
    if not self._waiter.wait(timeout = 1.0):
      raise RuntimeError('Failed to bind to address %s' % (str(self._address)))

    reactor.callFromThread(self.started)

    self.log_i('Bound to address %s' % (str(self._address)))

  @synchronized_method('_lock')
  def stop(self):
    if not self._thread:
      return
    stopped_waiter = Waiter()
    reactor.callFromThread(self.__call_stopped, stopped_waiter)
    
    if not stopped_waiter.wait(timeout = 1.0):
      self.log_e('Failed to call stopped')

    reactor.callFromThread(reactor.stop)

    self._thread.join()
    self._thread = None

  def __thread_main(self):
    self.log_i('__thread_main: self=%s' % (self))
    self.bind()
    self._waiter.notify()
    self.log_i('reactor now running.')
    try:
      reactor.run(installSignalHandlers = False)
    except ReactorAlreadyRunning, ex:
      pass

  def __call_stopped(self, waiter):
    self.stopped()
    waiter.notify()

  def bind(self):
    self.log_e('MessageServer.bind(%s) unimplemented' % (self))
    assert False, 'Not implemented'

  def started(self):
    'Called when the server is started.'
    pass

  def stopped(self):
    'Called when the server is stopped.'
    pass
