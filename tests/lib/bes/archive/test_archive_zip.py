#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.archive.archive_extension import archive_extension
from bes.archive.temp_archive import temp_archive
from bes.archive.archive_zip import archive_zip

from archive_tester import make_test_case

class test_archive_zip(make_test_case(archive_zip, archive_extension.ZIP)):

    @classmethod
    def setUpClass(clazz):
      pass

    def test_init(self):
      self.assertEqual( 'foo.zip', archive_zip('foo.zip').filename )
  
    def test_file_is_valid(self):
      tmp_zip = temp_archive.make_temp_archive([ temp_archive.item('foo.txt', content = 'foo.txt\n') ], archive_extension.ZIP)
      self.assertTrue( archive_zip.file_is_valid(tmp_zip) )
  
      tmp_tar = temp_archive.make_temp_archive([ temp_archive.item('foo.txt', content = 'foo.txt\n') ], archive_extension.TAR)
      self.assertFalse( archive_zip.file_is_valid(tmp_tar) )
  
      tmp_tgz = temp_archive.make_temp_archive([ temp_archive.item('foo.txt', content = 'foo.txt\n') ], archive_extension.TGZ)
      self.assertFalse( archive_zip.file_is_valid(tmp_tgz) )
  
      tmp_tar_gz = temp_archive.make_temp_archive([ temp_archive.item('foo.txt', content = 'foo.txt\n') ], archive_extension.TAR_GZ)
      self.assertFalse( archive_zip.file_is_valid(tmp_tar_gz) )
  
      self.assertFalse( archive_zip.file_is_valid(self.make_temp_file(content = 'junk\n')) )

if __name__ == '__main__':
  unit_test.main()
