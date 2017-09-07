#!/usr/bin/env python
#-*- coding:utf-8 -*-
#
import unittest

from bes.system import host
from bes.system import impl_import
from bes.unit_test.unit_test_skip import skip_if

def _load(impl_name):
  clazz = impl_import.load('something', globals())
  obj = clazz()
  return obj

class test_impl_import(unittest.TestCase):

  @skip_if(not host.is_macos(), 'not macos')
  def test_something_macos(self):
    obj = _load('something')
    self.assertEqual( 'steve', obj.creator() )
    self.assertEqual( 9, obj.suck_level() )

  @skip_if(not host.is_linux(), 'not linux')
  def test_something_linux(self):
    obj = _load('something')
    self.assertEqual( 'linus', obj.creator() )
    self.assertEqual( 8, obj.suck_level() )

  from something_base import something_base
  class something(something_base):
    def __init__(self):
      self.__impl = _load(test_impl_import.something)
    def creator(self):
      return self.__impl.creator()
    def suck_level(self):
      return self.__impl.suck_level()

  from something_base import something_base
  class something_static(something_base):
    __impl = _load('something')
    @classmethod
    def creator(clazz):
      return clazz.__impl.creator()
    @classmethod
    def suck_level(clazz):
      return clazz.__impl.suck_level()

  @skip_if(not host.is_macos(), 'not macos')
  def test_something_macos_reference_wrapper(self):
    obj = test_impl_import.something()
    self.assertEqual( 'steve', obj.creator() )
    self.assertEqual( 9, obj.suck_level() )

  @skip_if(not host.is_macos(), 'not macos')
  def test_something_macos_reference_wrapper_static(self):
    self.assertEqual( 'steve', test_impl_import.something_static.creator() )
    self.assertEqual( 9, test_impl_import.something_static.suck_level() )

if __name__ == "__main__":
  unittest.main()
