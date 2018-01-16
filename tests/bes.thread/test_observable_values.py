#!/usr/bin/env python
#-*- coding:utf-8 -*-
#
import unittest
from bes.thread import ObservableValues, thread_pool, Waiter

class test_observable_values(unittest.TestCase):

  def test_foo(self):
    d = ObservableValues()
    d['foo'] = 666
    d['foo'] = 666
#    print d['foo']
#    print d['bar']

  def test_caca(self):
    d = ObservableValues()

    def foo_setter(key, value):
      pass #print "setter(key=%s, value=%s)" % (key, value)

    def foo_getter(key):
      pass #print "getter(key=%s)" % (key)

    d.add_property('foo', foo_setter, foo_getter)

    #d.foo = 666
    

  def test_observer(self):
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
