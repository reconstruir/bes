#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.testing.unit_test import unit_test
from bes.fs.file_checksum import new_file_checksum as FC
from bes.fs.file_checksum import file_checksum_list as FCL
  
class test_file_checksum(unit_test):

  __unit_test_data_dir__ = '${BES_TEST_DATA_DIR}/bes.fs/file_checksum'

  def test_from_file(self):
    self.assertEqual( ( 'a.txt', '9124d0084fc1decd361e82332f535e6371496ceb' ), FC.from_file('a.txt', root_dir = self.data_dir()) )
    self.assertEqual( ( 'b.txt', 'fad3eb80ab58ca9a60249700b85aacf727395e1d' ), FC.from_file('b.txt', root_dir = self.data_dir()) )
    
  def test_from_files(self):
    self.assertEqual( [
      ( 'a.txt', '9124d0084fc1decd361e82332f535e6371496ceb' ),
      ( 'b.txt', 'fad3eb80ab58ca9a60249700b85aacf727395e1d' ),
    ], FCL.from_files([ 'a.txt', 'b.txt' ], root_dir = self.data_dir()) )
    
  def test_to_json(self):
    expected = '''\
[
  [
    "a.txt", 
    "9124d0084fc1decd361e82332f535e6371496ceb"
  ], 
  [
    "b.txt", 
    "fad3eb80ab58ca9a60249700b85aacf727395e1d"
  ]
]'''
    self.assertMultiLineEqual( expected, FCL.from_files([ 'a.txt', 'b.txt' ], root_dir = self.data_dir()).to_json() )
    
  def test_from_json(self):
    expected = FCL([ FC('a.txt', '9124d0084fc1decd361e82332f535e6371496ceb'), FC('b.txt', 'fad3eb80ab58ca9a60249700b85aacf727395e1d') ])
    json = '''\
[
  [
    "a.txt", 
    "9124d0084fc1decd361e82332f535e6371496ceb"
  ], 
  [
    "b.txt", 
    "fad3eb80ab58ca9a60249700b85aacf727395e1d"
  ]
]'''
    self.assertEqual( expected, FCL.from_json(json) )
    
if __name__ == '__main__':
  unit_test.main()
    
