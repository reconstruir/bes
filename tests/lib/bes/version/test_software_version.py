#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.version.software_version import software_version as VC
from bes.version.semantic_version_error import semantic_version_error

class test_software_version(unit_test):

  def test_compare(self):
    self.assertEqual( -1, VC.compare('1.2.3', '1.2.4') )
    self.assertEqual(  0, VC.compare('1.2.3', '1.2.3') )
    self.assertEqual(  1, VC.compare('1.2.4', '1.2.3') )
    self.assertEqual( -1, VC.compare('1.2.8', '1.2.9') )
    self.assertEqual( -1, VC.compare('1.2.10', '1.2.11') )
    self.assertEqual( -1, VC.compare('1.2.9', '1.2.10') )
    self.assertEqual( -1, VC.compare('3.0.4', '3.3') )
    
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
 
  def test_bump_version(self):
    self.assertEqual( '1.0.1', VC.bump_version('1.0.0', VC.REVISION) )
 
  def test_bump_version_major_reset_lower(self):
    self.assertEqual( '2.0.0', VC.bump_version('1.0.0', VC.MAJOR, reset_lower = True) )
    self.assertEqual( '2.0.0', VC.bump_version('1.0.1', VC.MAJOR, reset_lower = True) )
    self.assertEqual( '2.0.0', VC.bump_version('1.1.0', VC.MAJOR, reset_lower = True) )
    self.assertEqual( '2.0.0', VC.bump_version('1.1.1', VC.MAJOR, reset_lower = True) )
    self.assertEqual( '2.0.0', VC.bump_version('1.0.0', VC.MAJOR, reset_lower = True) )
    self.assertEqual( '2.0.0', VC.bump_version('1.0.1', VC.MAJOR, reset_lower = True) )
    self.assertEqual( '2.0.0', VC.bump_version('1.1.0', VC.MAJOR, reset_lower = True) )
    self.assertEqual( '2.0.0', VC.bump_version('1.1.1', VC.MAJOR, reset_lower = True) )
 
  def test_bump_version_minor_reset_lower(self):
    self.assertEqual( '1.1.0', VC.bump_version('1.0.0', VC.MINOR, reset_lower = True) )
#    self.assertEqual( '1.1.0', VC.bump_version('1.0.1', VC.MINOR, reset_lower = True) )
#    self.assertEqual( '1.2.0', VC.bump_version('1.1.1', VC.MINOR, reset_lower = True) )
#    self.assertEqual( '1.1.0', VC.bump_version('1.0.0', VC.MINOR, reset_lower = True) )
#    self.assertEqual( '1.1.0', VC.bump_version('1.0.1', VC.MINOR, reset_lower = True) )
#    self.assertEqual( '1.2.0', VC.bump_version('1.1.1', VC.MINOR, reset_lower = True) )
 
  def test_bump_version_revision_reset_lower(self):
    self.assertEqual( '1.0.1', VC.bump_version('1.0.0', VC.REVISION, reset_lower = True) )
    self.assertEqual( '1.1.1', VC.bump_version('1.1.0', VC.REVISION, reset_lower = True) )
    self.assertEqual( '1.0.1', VC.bump_version('1.0.0', VC.REVISION, reset_lower = True) )
    self.assertEqual( '1.1.1', VC.bump_version('1.1.0', VC.REVISION, reset_lower = True) )

  def test_bump_version_major(self):
    self.assertEqual( '2.0.0', VC.bump_version('1.0.0', VC.MAJOR) )
    self.assertEqual( '2.0.1', VC.bump_version('1.0.1', VC.MAJOR) )
    self.assertEqual( '2.1.0', VC.bump_version('1.1.0', VC.MAJOR) )
    self.assertEqual( '2.1.1', VC.bump_version('1.1.1', VC.MAJOR) )
    self.assertEqual( '2.0.0', VC.bump_version('1.0.0', VC.MAJOR) )
    self.assertEqual( '2.0.1', VC.bump_version('1.0.1', VC.MAJOR) )
    self.assertEqual( '2.1.0', VC.bump_version('1.1.0', VC.MAJOR) )
    self.assertEqual( '2.1.1', VC.bump_version('1.1.1', VC.MAJOR) )
 
  def test_bump_version_minor(self):
    self.assertEqual( '1.1.0', VC.bump_version('1.0.0', VC.MINOR) )
    self.assertEqual( '1.1.1', VC.bump_version('1.0.1', VC.MINOR) )
    self.assertEqual( '1.2.1', VC.bump_version('1.1.1', VC.MINOR) )
    self.assertEqual( '1.1.0', VC.bump_version('1.0.0', VC.MINOR) )
    self.assertEqual( '1.1.1', VC.bump_version('1.0.1', VC.MINOR) )
    self.assertEqual( '1.2.1', VC.bump_version('1.1.1', VC.MINOR) )
 
  def test_bump_version_revision(self):
    self.assertEqual( '1.0.1', VC.bump_version('1.0.0', VC.REVISION) )
    self.assertEqual( '1.1.1', VC.bump_version('1.1.0', VC.REVISION) )
    self.assertEqual( '1.0.1', VC.bump_version('1.0.0', VC.REVISION) )
    self.assertEqual( '1.1.1', VC.bump_version('1.1.0', VC.REVISION) )

  def test_bump_version_invalid_component(self):
    with self.assertRaises(semantic_version_error) as _:
      VC.bump_version('1.0.0', 3)
    
  def test_bump_version_major_two_components(self):
    self.assertEqual( '2.0', VC.bump_version('1.0', VC.MAJOR) )
    self.assertEqual( '2.1', VC.bump_version('1.1', VC.MAJOR) )

  def test_bump_version_minor_two_components(self):
    self.assertEqual( '1.1', VC.bump_version('1.0', VC.MINOR) )
    self.assertEqual( '1.2', VC.bump_version('1.1', VC.MINOR) )

  def test_bump_version_major_two_components_invalid_component(self):
    with self.assertRaises(semantic_version_error) as _:
      VC.bump_version('1.0', VC.REVISION)
    
  def test_bump_version_major_one_component(self):
    self.assertEqual( '2', VC.bump_version('1', VC.MAJOR) )
    self.assertEqual( '3', VC.bump_version('2', VC.MAJOR) )
 
  def test_bump_version_major_one_component_invalid_component(self):
    with self.assertRaises(semantic_version_error) as _:
      VC.bump_version('1', VC.MINOR)
    with self.assertRaises(semantic_version_error) as _:
      VC.bump_version('1', VC.REVISION)

  def test_change_component(self):
    self.assertEqual( '1.2.3', VC.change_component('1.2.2', VC.REVISION, '3') )
    self.assertEqual( '1.3.2', VC.change_component('1.2.2', VC.MINOR, '3') )
    self.assertEqual( '3.2.2', VC.change_component('1.2.2', VC.MAJOR, '3') )
    self.assertEqual( '1.2.3', VC.change_component('1.2.2', 'revision', '3') )
    self.assertEqual( '1.3.2', VC.change_component('1.2.2', 'minor', '3') )
    self.assertEqual( '3.2.2', VC.change_component('1.2.2', 'major', '3') )
    self.assertEqual( '1.2.3', VC.change_component('1.2.2', 2, '3') )
    self.assertEqual( '1.3.2', VC.change_component('1.2.2', 1, '3') )
    self.assertEqual( '3.2.2', VC.change_component('1.2.2', 0, '3') )
    self.assertEqual( '3-2-2', VC.change_component('1-2-2', 0, '3') )

    with self.assertRaises(semantic_version_error) as _:
      VC.change_component('1.2.2', 4, '3')

  def test_parse_version(self):
    self.assertEqual( ( ( 1, 0, 1 ), '.' ), VC.parse_version('1.0.1') )
    self.assertEqual( ( ( 1, 0, 2 ), '.' ), VC.parse_version('1.0.2') )
    self.assertEqual( ( ( 1, 0, 2, 3 ), '.' ), VC.parse_version('1.0.2.3') )
    self.assertEqual( ( ( 1, 0, 11 ), '.' ), VC.parse_version('1.0.11') )
    self.assertEqual( ( ( 1, 0 ), '.' ), VC.parse_version('1.0') )
    self.assertEqual( ( ( 1, ), '' ), VC.parse_version('1') )
      
if __name__ == "__main__":
  unit_test.main()
