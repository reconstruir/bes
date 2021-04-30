#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.python.python_version import python_version

class test_python_version(unit_test):

  def test___str__(self):
    self.assertEqual( '1.2.3', str(python_version('1.2.3')) )
    self.assertEqual( '1.2', str(python_version('1.2')) )
    self.assertEqual( '1', str(python_version('1')) )

  def test___len__(self):
    self.assertEqual( 3, len(python_version('1.2.3')) )
    self.assertEqual( 2, len(python_version('1.2')) )
    self.assertEqual( 1, len(python_version('1')) )

  def test___eq__(self):
    self.assertTrue( python_version('1.2.3') == python_version('1.2.3') )
    self.assertFalse( python_version('1.2.3') == python_version('1.2.4') )
    
  def test_parts(self):
    self.assertEqual( ( 1, 2, 3 ), python_version('1.2.3').parts )
    self.assertEqual( ( 1, 2 ), python_version('1.2').parts )
    self.assertEqual( ( 1, ), python_version('1').parts )

  def test_major_version(self):
    self.assertEqual( python_version('1'), python_version('1.2.3').major_version )
    self.assertEqual( python_version('1'), python_version('1.2').major_version )
    self.assertEqual( python_version('1'), python_version('1').major_version )
    
  def test_version(self):
    self.assertEqual( python_version('1.2'), python_version('1.2.3').version )
    self.assertEqual( python_version('1.2'), python_version('1.2').version )
    
  def test_full_version(self):
    self.assertEqual( python_version('1.2.3'), python_version('1.2.3').full_version )
    
  def test_is_version(self):
    self.assertTrue( python_version('6.7').is_version() )
    self.assertFalse( python_version('6.7.8').is_version() )

  def test_is_full_version(self):
    self.assertTrue( python_version('6.7.8').is_full_version() )
    self.assertFalse( python_version('6.7').is_full_version() )

  def test_is_major_version(self):
    self.assertTrue( python_version('6').is_major_version() )
    self.assertFalse( python_version('6.7.8').is_major_version() )
    self.assertFalse( python_version('6.7').is_major_version() )
    
  def test_major(self):
    self.assertEqual( 6, python_version('6').major )
    self.assertEqual( 6, python_version('6.7').major )
    self.assertEqual( 6, python_version('6.8').major )
    
if __name__ == '__main__':
  unit_test.main()
