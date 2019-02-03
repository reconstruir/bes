#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.version.version_compare import version_compare as VC

class test_version_compare(unit_test):

  def test_compare(self):
    self.assertEqual( -1, VC.compare('1.2.3', '1.2.4') )
    self.assertEqual(  0, VC.compare('1.2.3', '1.2.3') )
    self.assertEqual(  1, VC.compare('1.2.4', '1.2.3') )
    self.assertEqual( -1, VC.compare('1.2.8', '1.2.9') )
    self.assertEqual( -1, VC.compare('1.2.10', '1.2.11') )
    self.assertEqual( -1, VC.compare('1.2.9', '1.2.10') )
    
    self.assertEqual(  1, VC.compare('1:1.2.3', '1.2.4') )
    self.assertEqual( -1, VC.compare('0:1.2.3', '1.2.4') )
    self.assertEqual( -1, VC.compare('0:1.2.3', '0:1.2.3-1') )
    self.assertEqual(  1, VC.compare('0:1.2.3-3', '0:1.2.3-2') )

    self.assertEqual(  1, VC.compare('1.2.3', '1.2-3') )
    self.assertEqual( -1, VC.compare('1.2-3', '1.2.3') )
    
  def test_sort_versions(self):
    self.assertEqual( [
      '1.0.1',
      '1.0.2',
      '1.0.9',
      '1.0.10',
      '1.0.100',
    ], VC.sort_versions( [
      '1.0.1',
      '1.0.10',
      '1.0.2',
      '1.0.100',
      '1.0.9',
    ] ) )
 
  def test_sort_versions_reversed(self):
    self.assertEqual( [
      '1.0.100',
      '1.0.10',
      '1.0.9',
      '1.0.2',
      '1.0.1',
    ], VC.sort_versions( [
      '1.0.1',
      '1.0.10',
      '1.0.2',
      '1.0.100',
      '1.0.9',
    ], reverse = True ) )
 
  def test_change_version(self):
    self.assertEqual( '1.0.1', VC.change_version('1.0.0', [ 0, 0, 1 ]) )
    self.assertEqual( '1.0.0', VC.change_version('1.0.1', [ 0, 0, -1 ]) )
    self.assertEqual( '2.0.0', VC.change_version('1.0.0', [ 1, 0, 0 ]) )
    self.assertEqual( '2.3.4', VC.change_version('1.2.3', [ 1, 1, 1 ]) )
    self.assertEqual( '2.3.4.0', VC.change_version('1.2.3.0', [ 1, 1, 1 ]) )
    self.assertEqual( '2.2.3.0', VC.change_version('1.2.3.0', [ 1 ]) )
 
  def test_version_range(self):
    self.assertEqual( [ '1.0.1', '1.0.2', '1.0.3' ], VC.version_range('1.0.1', '1.0.3', [ 0, 0, 1 ]) )
    self.assertEqual( [ '1.0.1' ], VC.version_range('1.0.1', '1.0.1', [ 0, 0, 1 ]) )
    self.assertEqual( [ '1.0.1', '1.0.2' ], VC.version_range('1.0.1', '1.0.2', [ 0, 0, 1 ]) )
    self.assertEqual( [ '1.0.8', '1.0.9', '1.0.10', '1.0.11' ], VC.version_range('1.0.8', '1.0.11', [ 0, 0, 1 ]) )
 
  def test_version_to_tuple(self):
    self.assertEqual( ( 1, 0, 1 ), VC.version_to_tuple('1.0.1') )
    self.assertEqual( ( 1, 0, 2 ), VC.version_to_tuple('1.0.2') )
    self.assertEqual( ( 1, 0, 2, 3 ), VC.version_to_tuple('1.0.2.3') )
    self.assertEqual( ( 1, 0, 11 ), VC.version_to_tuple('1.0.11') )
 
if __name__ == "__main__":
  unit_test.main()
