#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.system.shell_path import shell_path

class test_shell_path(unit_test):

  def test_split(self):
    self.assertEqual( [], shell_path.split(None) )
    self.assertEqual( [ 'a', 'b' ], shell_path.split(self.native_path('a:b')) )
    self.assertEqual( [ 'a' ], shell_path.split(self.native_path('a')) )
    self.assertEqual( [ 'a', 'b', 'a' ], shell_path.split(self.native_path('a:b:a')) )

  def test_join(self):
    self.assertEqual( self.native_path('a:b'), shell_path.join([ 'a', 'b' ] ) )
    self.assertEqual( self.native_path('a'), shell_path.join([ 'a' ]) )
    self.assertEqual( self.native_path('a:b:a'), shell_path.join([ 'a', 'b', 'a' ]) )
    
  def test_remove_duplicates(self):
    self.assertEqual( self.native_path(''), shell_path.remove_duplicates('') )
    self.assertEqual( self.native_path('a:b'), shell_path.remove_duplicates('a:b') )
    self.assertEqual( self.native_path('a'), shell_path.remove_duplicates('a') )
    self.assertEqual( self.native_path('a:b'), shell_path.remove_duplicates(self.native_path('a:b:a')) )

  def test_diff(self):
    self.assertEqual( ( [], [] ), self._call_diff('a:b', 'a:b') )
    self.assertEqual( ( [], [] ), self._call_diff('a:b', 'b:a') )
    self.assertEqual( ( [], [ 'b' ] ), self._call_diff('a:b', 'a') )
    self.assertEqual( ( [ 'c', 'd' ], [] ), self._call_diff('a:b', 'b:c:d:a') )

  def _call_diff(self, p1, p2):
    return shell_path.diff(self.native_path(p1), self.native_path(p2))
    
if __name__ == '__main__':
  unit_test.main()
