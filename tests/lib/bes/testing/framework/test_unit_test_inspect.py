#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.fs import file_util, temp_file
from bes.testing.unit_test import unit_test
from bes.testing.framework import unit_test_inspect as UTI
from bes.testing.unit_test.unit_test_skip import raise_skip
  
class test_unit_test_inspect(unit_test):

  @classmethod
  def setUpClass(clazz):
    raise_skip('broken')
  
  def test_inspect_file(self):
    content = '''
import unittest
class test_apple_fixture(unittest.TestCase):

  def test_foo(self):
    self.assertEqual( 6, 3 + 3 )

  def test_bar(self):
    self.assertEqual( 7, 3 + 4 )
'''
    filename = temp_file.make_temp_file(content = content, suffix = '.py')
    self.assertEqual( [
      ( filename, 'test_apple_fixture', 'test_foo' ),
      ( filename, 'test_apple_fixture', 'test_bar' ),
    ],
                      UTI.inspect_file(filename) )
    file_util.remove(filename)

  def test_inspect_file_not_unit_test(self):
    content = '''
class test_apple_fixture(object):

  def test_foo(self):
    pass

  def test_bar(self):
    pass
'''
    filename = temp_file.make_temp_file(content = content, suffix = '.py')
    self.assertEqual( [], UTI.inspect_file(filename) )
    file_util.remove(filename)

  def test_inspect_file_disbled(self):
    content = '''
import unittest
class test_apple_fixture(unittest.TestCase):

  def xtest_foo(self):
    self.assertEqual( 6, 3 + 3 )

  def xtest_bar(self):
    self.assertEqual( 7, 3 + 4 )
'''
    filename = temp_file.make_temp_file(content = content, suffix = '.py')
    self.assertEqual( [
    ],
                      UTI.inspect_file(filename) )
    file_util.remove(filename)


    
  def doesnt_work_test_inspect_file_TestCase_subclass(self):
    content = '''
import unittest
class unit_super(unittest.TestCase):
  _x = 5
class test_apple_fixture(unit_super):

  def test_foo(self):
    self.assertEqual( 6, 3 + 3 )

  def test_bar(self):
    self.assertEqual( 7, 3 + 4 )


class somthing(unittest.TestCase):
  pass
'''
    filename = temp_file.make_temp_file(content = content, suffix = '.py')
    self.assertEqual( [
      ( filename, 'test_apple_fixture', 'test_foo' ),
      ( filename, 'test_apple_fixture', 'test_bar' ),
    ],
                      UTI.inspect_file(filename) )
    file_util.remove(filename)
    
  def test_inspect_file_unit_test(self):
    content = '''
from bes.testing.unit_test import unit_test
class test_apple_fixture(unit_test):

  def test_foo(self):
    self.assertEqual( 6, 3 + 3 )

  def test_bar(self):
    self.assertEqual( 7, 3 + 4 )
'''
    filename = temp_file.make_temp_file(content = content, suffix = '.py')
    self.assertEqual( [
      ( filename, 'test_apple_fixture', 'test_foo' ),
      ( filename, 'test_apple_fixture', 'test_bar' ),
    ],
                      UTI.inspect_file(filename) )
    file_util.remove(filename)
    
if __name__ == '__main__':
  unit_test.main()
    
