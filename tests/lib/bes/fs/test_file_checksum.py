#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.testing.unit_test import unit_test
from bes.fs.file_checksum import file_checksum as FC, file_checksum_list as FCL
from bes.fs import file_checksum, file_util, temp_file
  
class test_file_checksum(unit_test):

  __unit_test_data_dir__ = '${BES_TEST_DATA_DIR}/bes.fs/file_checksum'

  A_CHK = '7bf1c5c4153ecb5364b0c7fcb2e767fadc6880e0c2620b69df56b6bb5429448d'
  B_CHK = '429340c7abf63fe50eb3076d3f1d5d996f3b4ee3067734ae8832129af244653c'
  
  def test_from_file(self):
    self.assertEqual( ( 'a.txt', self.A_CHK ), FC.from_file('a.txt', root_dir = self.data_dir()) )
    self.assertEqual( ( 'b.txt', '429340c7abf63fe50eb3076d3f1d5d996f3b4ee3067734ae8832129af244653c' ), FC.from_file('b.txt', root_dir = self.data_dir()) )
    
  def test_from_files(self):
    self.assertEqual( [
      ( 'a.txt', self.A_CHK ),
      ( 'b.txt', self.B_CHK ),
    ], FCL.from_files([ 'a.txt', 'b.txt' ], root_dir = self.data_dir()) )

  def test_list_from_tuples(self):
    l = FCL([
      ( 'a.txt', self.A_CHK ),
      ( 'b.txt', self.B_CHK ),
    ])
    self.assertEqual( l, FCL.from_files([ 'a.txt', 'b.txt' ], root_dir = self.data_dir()))
    
  def test_to_json(self):
    expected = '''\
[
  [
    "a.txt", 
    "7bf1c5c4153ecb5364b0c7fcb2e767fadc6880e0c2620b69df56b6bb5429448d"
  ], 
  [
    "b.txt", 
    "429340c7abf63fe50eb3076d3f1d5d996f3b4ee3067734ae8832129af244653c"
  ]
]'''
    self.assertEqualIgnoreWhiteSpace( expected, FCL.from_files([ 'a.txt', 'b.txt' ], root_dir = self.data_dir()).to_json() )
    
  def test_from_json(self):
    expected = FCL([ FC('a.txt', self.A_CHK), FC('b.txt', self.B_CHK) ])
    json = '''\
[
  [
    "a.txt", 
    "7bf1c5c4153ecb5364b0c7fcb2e767fadc6880e0c2620b69df56b6bb5429448d"
  ], 
  [
    "b.txt", 
    "429340c7abf63fe50eb3076d3f1d5d996f3b4ee3067734ae8832129af244653c"
  ]
]'''
    self.assertEqual( expected, FCL.from_json(json) )
    
  def test_filenames(self):
    a = FCL([ FC('a.txt', self.A_CHK), FC('b.txt', self.B_CHK) ])
    self.assertEqual( [ 'a.txt', 'b.txt' ], a.filenames() )
    
  def test_file_checksum(self):
    self.assertEqual( self.A_CHK, FC.file_checksum(self.data_path('a.txt'), 'sha256') )
    self.assertEqual( self.B_CHK, FC.file_checksum(self.data_path('b.txt'), 'sha256') )

  def test_save_checksums_file(self):
    tmp_file = temp_file.make_temp_file()
    a = FCL.from_files([ 'a.txt', 'b.txt' ], root_dir = self.data_dir())
    a.save_checksums_file(tmp_file)
    expected = '''\
[
  [
    "a.txt", 
    "7bf1c5c4153ecb5364b0c7fcb2e767fadc6880e0c2620b69df56b6bb5429448d"
  ], 
  [
    "b.txt", 
    "429340c7abf63fe50eb3076d3f1d5d996f3b4ee3067734ae8832129af244653c"
  ]
]'''
    self.assertEqual( expected, file_util.read(tmp_file, codec = 'utf8') )

  def test_load_checksums_file(self):
    content = '''\
[
  [
    "a.txt", 
    "7bf1c5c4153ecb5364b0c7fcb2e767fadc6880e0c2620b69df56b6bb5429448d"
  ], 
  [
    "b.txt", 
    "429340c7abf63fe50eb3076d3f1d5d996f3b4ee3067734ae8832129af244653c"
  ]
]'''
    tmp_file = temp_file.make_temp_file(content = content)
    expected = FCL.from_files([ 'a.txt', 'b.txt' ], root_dir = self.data_dir())
    self.assertEqual( expected, FCL.load_checksums_file(tmp_file) )

  def test_verify_true(self):
    a = FCL([ FC('a.txt', self.A_CHK), FC('b.txt', self.B_CHK) ])
    b = FCL([ FC('a.txt', self.A_CHK), FC('b.txt', self.B_CHK) ])
    self.assertTrue( a == b )
    
  def test_verify_false(self):
    a = FCL([ FC('a.txt', 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'), FC('b.txt', self.B_CHK) ])
    b = FCL([ FC('a.txt', self.A_CHK), FC('b.txt', self.B_CHK) ])
    self.assertFalse( a == b )
    
  def test_checksum(self):
    a = FCL([ FC('a.txt', 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'), FC('b.txt', self.B_CHK) ])
    self.assertEqual( '07981e316ef1eefdc58cc3fe5b34e9a51652a9178f25417111baeca29d9193f8', a.checksum() )
    
if __name__ == '__main__':
  unit_test.main()
    
