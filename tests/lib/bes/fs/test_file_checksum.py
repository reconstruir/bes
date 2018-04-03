#!/usr/bin/env python
#-*- coding:utf-8 -*-
#
from bes.testing.unit_test import unit_test
from bes.fs import file_checksum, file_util, temp_file

class test_file_checksum(unit_test):

  def test_checksum(self):
    tmp_file = temp_file.make_temp_file(content = 'foo\n')
    self.assertEqual( file_checksum.Item(tmp_file, 'f1d2d2f924e986ac86fdf7b36c94bcdf32beec15'), file_checksum.checksum(tmp_file) )

  def test_checksums(self):
    tmp_files = [
      temp_file.make_temp_file(content = 'foo\n'),
      temp_file.make_temp_file(content = 'bar\n'),
    ]
    expected_checksums = [
      file_checksum.Item(tmp_files[0], 'f1d2d2f924e986ac86fdf7b36c94bcdf32beec15'),
      file_checksum.Item(tmp_files[1], 'e242ed3bffccdf271b7fbaf34ed72d089537b42f'),
    ]
    self.assertEqual( expected_checksums, file_checksum.checksums(tmp_files) )

  def test_save_checksums(self):
    self.maxDiff = None
    tmp_files = [
      temp_file.make_temp_file(content = 'foo\n'),
      temp_file.make_temp_file(content = 'bar\n'),
    ]
    expected_checksums = [
      file_checksum.Item(tmp_files[0], 'f1d2d2f924e986ac86fdf7b36c94bcdf32beec15'),
      file_checksum.Item(tmp_files[1], 'e242ed3bffccdf271b7fbaf34ed72d089537b42f'),
    ]
    checksums = file_checksum.checksums(tmp_files)
    tmp_checksums_filename = temp_file.make_temp_file()
    file_checksum.save_checksums(tmp_checksums_filename, checksums)

    expected_json = '''[
  [
    "%s", 
    "f1d2d2f924e986ac86fdf7b36c94bcdf32beec15"
  ], 
  [
    "%s", 
    "e242ed3bffccdf271b7fbaf34ed72d089537b42f"
  ]
]''' % (expected_checksums[0].filename, expected_checksums[1].filename)

    import codecs
    actual_json = file_util.read(tmp_checksums_filename)
    actual_json = codecs.decode(actual_json, 'utf-8')
    self.assertEqualIgnoreWhiteSpace( expected_json, actual_json )

  def test_load_checksums(self):
    json = '''[
  [
    "/foo/bar/something.txt", 
    "f1d2d2f924e986ac86fdf7b36c94bcdf32beec15"
  ], 
  [
    "/foo/bar/nothing.txt", 
    "e242ed3bffccdf271b7fbaf34ed72d089537b42f"
  ]
]'''

    tmp_json_filename = temp_file.make_temp_file(content = json)

    expected_checksums = [
      file_checksum.Item('/foo/bar/something.txt', 'f1d2d2f924e986ac86fdf7b36c94bcdf32beec15'),
      file_checksum.Item('/foo/bar/nothing.txt', 'e242ed3bffccdf271b7fbaf34ed72d089537b42f'),
    ]
    actual_checksums = file_checksum.load_checksums(tmp_json_filename)
    self.assertEqual( expected_checksums, actual_checksums )

  def test_load_checksums_missing_filename(self):
    self.assertEqual( None, file_checksum.load_checksums('/notthereihopeitaint') )

  def test_verify(self):
    tmp_file = temp_file.make_temp_file(content = 'foo\n')
    checksum = file_checksum.checksum(tmp_file)
    self.assertTrue( file_checksum.verify(checksum) )

if __name__ == '__main__':
  unit_test.main()
