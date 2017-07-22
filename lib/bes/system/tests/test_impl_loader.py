#!/usr/bin/env python
#-*- coding:utf-8 -*-
#
import unittest

from bes.system import host
from bes.system import impl_loader
from bes.test.unit_test_skip import skip_if

class test_impl_loader(unittest.TestCase):

  @skip_if(not host.is_macos(), 'not macos')
  def test_something_macos(self):
    obj = impl_loader.load(__file__, 'something')
    self.assertEqual( 'steve', obj.creator() )
    self.assertEqual( 9, obj.suck_level() )

  @skip_if(not host.is_linux(), 'not linux')
  def test_something_linux(self):
    obj = impl_loader.load(__file__, 'something')
    self.assertEqual( 'linus', obj.creator() )
    self.assertEqual( 8, obj.suck_level() )

  @skip_if(not host.is_macos(), 'not macos')
  def test_something_macos_reference_object(self):
    obj = impl_loader.load(test_impl_loader, 'something')
    self.assertEqual( 'steve', obj.creator() )
    self.assertEqual( 9, obj.suck_level() )

  @skip_if(not host.is_linux(), 'not linux')
  def test_something_linux_reference_object(self):
    obj = impl_loader.load(test_impl_loader, 'something')
    self.assertEqual( 'linus', obj.creator() )
    self.assertEqual( 8, obj.suck_level() )

  from something_base import something_base
  class something(something_base):
    def __init__(self):
      self.__impl = impl_loader.load(test_impl_loader.something)
    def creator(self):
      return self.__impl.creator()
    def suck_level(self):
      return self.__impl.suck_level()

  from something_base import something_base
  class something_static(something_base):
    __impl = impl_loader.load(__file__, 'something')
    @classmethod
    def creator(clazz):
      return clazz.__impl.creator()
    @classmethod
    def suck_level(clazz):
      return clazz.__impl.suck_level()

  @skip_if(not host.is_macos(), 'not macos')
  def test_something_macos_reference_wrapper(self):
    obj = test_impl_loader.something()
    self.assertEqual( 'steve', obj.creator() )
    self.assertEqual( 9, obj.suck_level() )

  @skip_if(not host.is_linux(), 'not linux')
  def test_something_linux_reference_object(self):
    obj = test_impl_loader.something()
    self.assertEqual( 'linus', obj.creator() )
    self.assertEqual( 8, obj.suck_level() )

  @skip_if(not host.is_macos(), 'not macos')
  def test_something_macos_reference_wrapper_static(self):
    self.assertEqual( 'steve', test_impl_loader.something_static.creator() )
    self.assertEqual( 9, test_impl_loader.something_static.suck_level() )

  @skip_if(not host.is_linux(), 'not linux')
  def test_something_linux_reference_object_static(self):
    self.assertEqual( 'linus', test_impl_loader.something_static.creator() )
    self.assertEqual( 8, test_impl_loader.something_static.suck_level() )

if __name__ == "__main__":
  unittest.main()
