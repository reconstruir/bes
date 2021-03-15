#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os

from bes.testing.unit_test import unit_test
from bes.system.env_var import os_env_var

class test_os_env_var(unit_test):

  TEST_NAME = 'NOTHEREIHOPEORELSETHISFAILS'

  __test_name_count = 0

  @classmethod
  def __test_name(clazz):
    clazz.__test_name_count += 1
    return '%s_%s_%s' % (clazz.TEST_NAME, os.getpid(), clazz.__test_name_count)

  def test_get_unknown(self):
    test_name = self.__test_name()
    self.assertEqual( None, os_env_var(test_name).value )

  def test_set(self):
    test_name = self.__test_name()
    v = os_env_var(test_name)
    v.value = 'FOO'
    self.assertEqual( 'FOO', os.environ[test_name] )

  def test_get(self):
    test_name = self.__test_name()
    v = os_env_var(test_name)
    v.value = 'FOO'
    self.assertEqual( 'FOO', v.value )

  def test_get_environ(self):
    test_name = self.__test_name()
    os.environ[test_name] = 'FOO'
    self.assertEqual( 'FOO', os_env_var(test_name).value )

  def test_get_unknown_path(self):
    test_name = self.__test_name()
    self.assertEqual( [], os_env_var(test_name).path )

  def test_set_path(self):
    test_name = self.__test_name()
    v = os_env_var(test_name)
    v.path = [ 'FOO', 'BAR' ]
    self.assertEqual( 'FOO%sBAR' % (os.pathsep), os.environ[test_name] )

  def test_get_path(self):
    test_name = self.__test_name()
    v = os_env_var(test_name)
    v.path = [ 'FOO', 'BAR' ]
    self.assertEqual( [ 'FOO', 'BAR' ], v.path )

  def test_get_environ_path(self):
    test_name = self.__test_name()
    os.environ[test_name] = self.native_filename('FOO:BAR')
    self.assertEqual( [ 'FOO', 'BAR' ], os_env_var(test_name).path )

  def test_set_path_with_cleanup(self):
    test_name = self.__test_name()
    v = os_env_var(test_name)
    v.path = [ 'FOO', 'BAR', 'FOO' ]
    self.assertEqual( [ 'FOO', 'BAR' ], os_env_var(test_name).path )

  def test_append(self):
    test_name = self.__test_name()
    v = os_env_var(test_name)
    v.path = [ 'FOO', 'BAR' ]
    v.append('BAZ')
    self.assertEqual( [ 'FOO', 'BAR', 'BAZ' ], os_env_var(test_name).path )

  def test_append_duplicate(self):
    test_name = self.__test_name()
    v = os_env_var(test_name)
    v.path = [ 'FOO', 'BAR' ]
    v.append('FOO')
    self.assertEqual( [ 'BAR', 'FOO' ], os_env_var(test_name).path )

  def test_prepend(self):
    test_name = self.__test_name()
    v = os_env_var(test_name)
    v.path = [ 'FOO', 'BAR' ]
    v.prepend('BAZ')
    self.assertEqual( [ 'BAZ', 'FOO', 'BAR' ], os_env_var(test_name).path )

  def test_prepend_duplicate(self):
    test_name = self.__test_name()
    v = os_env_var(test_name)
    v.path = [ 'FOO', 'BAR', 'BAZ' ]
    v.prepend('BAR')
    self.assertEqual( [ 'BAR', 'FOO', 'BAZ' ], os_env_var(test_name).path )

  def test_path_cleanup(self):
    self.assertEqual( [ 'foo', 'bar' ], os_env_var.path_cleanup([ 'foo', 'bar' ]) )
    self.assertEqual( [ 'foo', 'bar' ], os_env_var.path_cleanup([ 'foo', 'bar', 'foo' ]) )

    self.assertEqual( [ 'foo', 'bar' ], os_env_var.path_cleanup([ 'foo', '', 'bar' ]) )

  def test_path_split(self):
    self.assertEqual( [ 'foo', 'bar' ], os_env_var.path_split(self.native_filename('foo:bar')) )
    self.assertEqual( [ 'foo', 'bar', 'bar' ], os_env_var.path_split(self.native_filename('foo:bar:bar')) )
    self.assertEqual( [ 'foo', 'bar', 'foo' ], os_env_var.path_split(self.native_filename('foo:bar:foo')) )

  def test_path_join(self):
    self.assertEqual( self.native_filename('foo:bar'), os_env_var.path_join([ 'foo', 'bar' ]) )
    self.assertEqual( self.native_filename('foo:bar:foo'), os_env_var.path_join([ 'foo', 'bar', 'foo' ]) )
    self.assertEqual( self.native_filename('foo:bar:bar'), os_env_var.path_join([ 'foo', 'bar', 'bar' ]) )

if __name__ == "__main__":
  unit_test.main()
