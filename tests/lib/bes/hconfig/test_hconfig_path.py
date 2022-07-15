#!/usr/bin/env python3
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.hconfig.hconfig_path import hconfig_path
from bes.hconfig.hconfig_error import hconfig_error

class test_hconfig_path(unit_test):

  def test_parts(self):
    self.assertEqual( [ 'a', 'b', 'c' ], hconfig_path('a.b.c').parts )

  def test__path_part_is_valid(self):
    self.assertEqual( True, hconfig_path._path_part_is_valid('kiwi', False) )
    self.assertEqual( False, hconfig_path._path_part_is_valid('', False) )
    self.assertEqual( True, hconfig_path._path_part_is_valid('kiwi2', False) )
    self.assertEqual( False, hconfig_path._path_part_is_valid('2kiwi', False) )
    self.assertEqual( True, hconfig_path._path_part_is_valid('_kiwi', False) )
    self.assertEqual( True, hconfig_path._path_part_is_valid('_', False) )
    self.assertEqual( True, hconfig_path._path_part_is_valid('_1', False) )
    self.assertEqual( False, hconfig_path._path_part_is_valid('1', False) )

  def test__path_part_is_valid_with_wildcards(self):
    self.assertEqual( False, hconfig_path._path_part_is_valid('', True) )
    self.assertEqual( True, hconfig_path._path_part_is_valid('kiwi*', True) )
    self.assertEqual( True, hconfig_path._path_part_is_valid('kiwi[a-d]', True) )
    self.assertEqual( True, hconfig_path._path_part_is_valid('kiwi?', True) )
    self.assertEqual( True, hconfig_path._path_part_is_valid('*kiwi', True) )
    self.assertEqual( True, hconfig_path._path_part_is_valid('kiw[!i]', True) )
    
  def test___getitem__(self):
    self.assertEqual( 'a', hconfig_path('a.b.c')[0] )
    self.assertEqual( 'b', hconfig_path('a.b.c')[1] )
    self.assertEqual( 'c', hconfig_path('a.b.c')[2] )
    
if __name__ == '__main__':
  unit_test.main()
