#!/usr/bin/env python
#-*- coding:utf-8 -*-

import unittest

from Scheduler import Scheduler
from functools import partial

class ObservableValues(object):
  """A dictionary with notifications for changes."""

  def __init__(self):
    super(ObservableValues, self).__init__()
    self._dict = {}
    self._observers = set()

  def __getitem__(self, key):
    return self._dict.get(key, None)
  
  def __setitem__(self, key, value):
    if self._dict.has_key(key) and self._dict[key] == value:
      return
    self._dict[key] = value
    self.__call_observers(key, value)

  def add_observer(self, observer):
    assert observer not in self._observers
    self._observers.add(observer)

  def remove_observer(self, observer):
    assert observer in self._observers
    self._observers.remove(observer)

  def __call_observers(self, key, value):
    for observer in self._observers:
      Scheduler.call_in_thread_pool(observer, key, value)

  def add_property(self, name, setter, getter):
    assert not self._dict.has_key(name) 
    prop = property(setter, getter)
    self.__setattr__(name, prop)

class TestObservableValues(unittest.TestCase):

  def test_foo(self):
    d = ObservableValues()
    d['foo'] = 666
    d['foo'] = 666
    print d['foo']
    print d['bar']

  def test_caca(self):
    d = ObservableValues()

    def foo_setter(key, value):
      print "setter(key=%s, value=%s)" % (key, value)

    def foo_getter(key):
      print "getter(key=%s)" % (key)

    d.add_property('foo', foo_setter, foo_getter)

    #d.foo = 666
    

  def test_observer(self):
    from Waiter import Waiter
    from ThreadPool import ThreadPool

    ThreadPool.start_global_thread_pool()

    d = ObservableValues()
    waiter = Waiter()
    def observer(key, value): waiter.notify()
    d.add_observer(observer)
    d['foo'] = 666
    self.assertEqual( True, waiter.wait() )

if __name__ == "__main__":
  unittest.main()

#remote.devices.dab.0.volume
#remote.devices.dab.0.muted
#remote.devices.dab.0.source
