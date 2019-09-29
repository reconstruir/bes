#!/usr/bin/env python3
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import hashlib

import os.path as path
from bes.testing.unit_test import unit_test
from bes.fs.file_checksum import file_checksum as FC
from bes.fs.file_checksum import file_checksum_list as FCL
from bes.fs.file_checksum import file_checksum
from bes.fs.file_util import file_util
from bes.fs.temp_file import temp_file
  
class test_file_checksum(unit_test):

  __unit_test_data_dir__ = '${BES_TEST_DATA_DIR}/lib/bes/fs/file_checksum'

  _DATA_1 = b'\xCA\xFE\xBA\xBE'
  _DATA_2 = b'\xDE\xAD\xBE\xEF'

  _FILE_1 = 'a.data'
  _FILE_2 = 'b.data'

  _CHK_1 = '65ab12a8ff3263fbc257e5ddf0aa563c64573d0bab1f1115b9b107834cfa6971'
  _CHK_2 = '5f78c33274e43fa9de5659265c1d917e25c03722dcb0b8d27db8d5feaa813953'
  
  def test_from_file(self):
    tmp_dir = self._make_test_data()
    self.assertEqual( ( self._FILE_1, self._CHK_1 ), FC.from_file(self._FILE_1, root_dir = tmp_dir) )
    self.assertEqual( ( self._FILE_2, self._CHK_2 ), FC.from_file(self._FILE_2, root_dir = tmp_dir) )
  
  def test_from_files(self):
    tmp_dir = self._make_test_data()
    self.assertEqual( [
      ( self._FILE_1, self._CHK_1 ),
      ( self._FILE_2, self._CHK_2 ),
    ], FCL.from_files([ self._FILE_1, self._FILE_2 ], root_dir = tmp_dir) )

  def test_list_from_tuples(self):
    tmp_dir = self._make_test_data()
    l = FCL([
      ( self._FILE_1, self._CHK_1 ),
      ( self._FILE_2, self._CHK_2 ),
    ])
    self.assertEqual( l, FCL.from_files([ self._FILE_1, self._FILE_2 ], root_dir = tmp_dir))
    
  def test_to_json(self):
    tmp_dir = self._make_test_data()
    expected = '''\
[
  [
    "a.data", 
    "65ab12a8ff3263fbc257e5ddf0aa563c64573d0bab1f1115b9b107834cfa6971"
  ], 
  [
    "b.data", 
    "5f78c33274e43fa9de5659265c1d917e25c03722dcb0b8d27db8d5feaa813953"
  ]
]'''
    self.assertEqualIgnoreWhiteSpace( expected, FCL.from_files([ self._FILE_1, self._FILE_2 ], root_dir = tmp_dir).to_json() )
    
  def test_from_json(self):
    expected = FCL([ FC(self._FILE_1, self._CHK_1), FC(self._FILE_2, self._CHK_2) ])
    json = '''\
[
  [
    "a.data", 
    "65ab12a8ff3263fbc257e5ddf0aa563c64573d0bab1f1115b9b107834cfa6971"
  ], 
  [
    "b.data", 
    "5f78c33274e43fa9de5659265c1d917e25c03722dcb0b8d27db8d5feaa813953"
  ]
]'''
    self.assertEqual( expected, FCL.from_json(json) )
    
  def test_filenames(self):
    a = FCL([ FC(self._FILE_1, self._CHK_1), FC(self._FILE_2, self._CHK_2) ])
    self.assertEqual( [ self._FILE_1, self._FILE_2 ], a.filenames() )
    
  def test_save_checksums_file(self):
    tmp_dir = self._make_test_data()
    tmp_file = temp_file.make_temp_file()
    a = FCL.from_files([ self._FILE_1, self._FILE_2 ], root_dir = tmp_dir)
    a.save_checksums_file(tmp_file)
    expected = '''\
[
  [
    "a.data", 
    "65ab12a8ff3263fbc257e5ddf0aa563c64573d0bab1f1115b9b107834cfa6971"
  ], 
  [
    "b.data", 
    "5f78c33274e43fa9de5659265c1d917e25c03722dcb0b8d27db8d5feaa813953"
  ]
]'''
    self.assertEqual( expected, file_util.read(tmp_file, codec = 'utf8') )

  def test_load_checksums_file(self):
    tmp_dir = self._make_test_data()
    content = '''\
[
  [
    "a.data", 
    "65ab12a8ff3263fbc257e5ddf0aa563c64573d0bab1f1115b9b107834cfa6971"
  ], 
  [
    "b.data", 
    "5f78c33274e43fa9de5659265c1d917e25c03722dcb0b8d27db8d5feaa813953"
  ]
]'''
    tmp_file = temp_file.make_temp_file(content = content)
    expected = FCL.from_files([ self._FILE_1, self._FILE_2 ], root_dir = tmp_dir)
    self.assertEqual( expected, FCL.load_checksums_file(tmp_file) )

  def test_verify_true(self):
    a = FCL([ FC(self._FILE_1, self._CHK_1), FC(self._FILE_2, self._CHK_2) ])
    b = FCL([ FC(self._FILE_1, self._CHK_1), FC(self._FILE_2, self._CHK_2) ])
    self.assertTrue( a == b )
    
  def test_verify_false(self):
    a = FCL([ FC(self._FILE_1, 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'), FC(self._FILE_2, self._CHK_2) ])
    b = FCL([ FC(self._FILE_1, self._CHK_1), FC(self._FILE_2, self._CHK_2) ])
    self.assertFalse( a == b )
    
  def test_checksum(self):
    a = FCL([ FC(self._FILE_1, 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'), FC(self._FILE_2, self._CHK_2) ])
    self.assertEqual( '829e15ebdca05bd85f09b3b1eab5eafbde9832b72d403a5e465cb7d86d796f6a', a.checksum() )

  @classmethod
  def _direct_checksum(clazz, filename):
    hasher = hashlib.new('sha256')
    with open(filename, 'rb') as fin: 
      hasher.update(fin.read())
    return hasher.hexdigest()
    
  def _test_data_checksum(self, filename):
    return self._direct_checksum(self.data_path(filename))
    
  def _test_a_checksum(self):
    return self._test_data_checksum(self._FILE_1)
    
  def _test_b_checksum(self):
    return self._test_data_checksum(self._FILE_1)

  @classmethod
  def _make_test_data(self):
    tmp_dir = self.make_temp_dir()
    file_util.save(path.join(tmp_dir, self._FILE_1), content = self._DATA_1)
    file_util.save(path.join(tmp_dir, self._FILE_2), content = self._DATA_2)
    return tmp_dir
  
if __name__ == '__main__':
  unit_test.main()
    
