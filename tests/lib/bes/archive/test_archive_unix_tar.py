#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.fs.temp_file import temp_file
from bes.archive.archive_extension import archive_extension
from bes.archive.temp_archive import temp_archive
from bes.archive.archive_unix_tar import archive_unix_tar
from bes.testing.unit_test_class_skip import unit_test_class_skip

from archive_tester import archive_tester

class test_archive_unix_tar(unit_test):

  @classmethod
  def _make_archive_tester(clazz, o):
    return archive_tester(o, archive_unix_tar, archive_extension.TAR, o.DEBUG)
  
  @classmethod
  def setUpClass(clazz):
    unit_test_class_skip.raise_skip('broken')
  
  def test_init(self):
    self.assertEqual( 'foo.tar', archive_unix_tar('foo.tar').filename )

  def test_file_is_valid(self):
    tmp_zip = temp_archive.make_temp_archive([ temp_archive.item('foo.txt', content = 'foo.txt\n') ], archive_extension.ZIP)
    self.assertFalse( archive_unix_tar.file_is_valid(tmp_zip) )

    tmp_tar = temp_archive.make_temp_archive([ temp_archive.item('foo.txt', content = 'foo.txt\n') ], archive_extension.TAR)
    self.assertTrue( archive_unix_tar.file_is_valid(tmp_tar) )

    tmp_tgz = temp_archive.make_temp_archive([ temp_archive.item('foo.txt', content = 'foo.txt\n') ], archive_extension.TGZ)
    self.assertTrue( archive_unix_tar.file_is_valid(tmp_tgz) )

    tmp_xz = temp_archive.make_temp_archive([ temp_archive.item('foo.txt', content = 'foo.txt\n') ], archive_extension.XZ)
    self.assertTrue( archive_unix_tar.file_is_valid(tmp_xz) )

    self.assertFalse( archive_unix_tar.file_is_valid(temp_file.make_temp_file(content = 'junk\n')) )

  def test_members(self):
    self._make_archive_tester(self).test_members()

  def test_has_member(self):
    return self._make_archive_tester(self).test_has_member()

  def test_extract_all(self):
    return self._make_archive_tester(self).test_extract_all()

  def test_extract_all_with_base_dir(self):
    return self._make_archive_tester(self).test_extract_all_with_base_dir()

  def test_extract_all_with_strip_common_ancestor(self):
    return self._make_archive_tester(self).test_extract_all_with_strip_common_ancestor()

  def test_extract_all_with_base_dir_and_strip_common_ancestor(self):
    return self._make_archive_tester(self).test_extract_all_with_base_dir_and_strip_common_ancestor()

  def test_extract_all_with_strip_head(self):
    return self._make_archive_tester(self).test_extract_all_with_strip_head()

  def test_extract_all_with_strip_common_ancestor_and_strip_head(self):
    return self._make_archive_tester(self).test_extract_all_with_strip_common_ancestor_and_strip_head()

  def test_extract_all_overlap(self):
    return self._make_archive_tester(self).test_extract_all_overlap()

  def test_extract_all_overlap_with_base_dir(self):
    return self._make_archive_tester(self).test_extract_all_overlap_with_base_dir()

  def test_extract_all_overlap_with_base_dir_and_strip_common_ancestor(self):
    return self._make_archive_tester(self).test_extract_all_overlap_with_base_dir_and_strip_common_ancestor()

  def test_extract_with_include(self):
    return self._make_archive_tester(self).test_extract_with_include()

  def test_extract_with_exclude(self):
    return self._make_archive_tester(self).test_extract_with_exclude()

  def test_extract_with_include_and_exclude(self):
    return self._make_archive_tester(self).test_extract_with_include_and_exclude()

  def test_extract_member_to_string(self):
    return self._make_archive_tester(self).test_extract_member_to_string()

  def test_extract_member_to_file(self):
    return self._make_archive_tester(self).test_extract_member_to_file()
    
  def test_extract_members(self):
    return self._make_archive_tester(self).test_extract_members()

  def test_common_base(self):
    return self._make_archive_tester(self).test_common_base()

  def test_common_base_none(self):
    return self._make_archive_tester(self).test_common_base_none()

  def test_create_basic(self):
    return self._make_archive_tester(self).test_create_basic()
    
  def test_create_base_dir(self):
    return self._make_archive_tester(self).test_create_base_dir()
    
  def test_create_with_include(self):
    return self._make_archive_tester(self).test_create_with_include()

  def test_create_with_multiple_include(self):
    return self._make_archive_tester(self).test_create_with_multiple_include()

  def test_create_with_exclude(self):
    return self._make_archive_tester(self).test_create_with_exclude()

  def test_create_with_multiple_exclude(self):
    return self._make_archive_tester(self).test_create_with_multiple_exclude()

  def test_create_with_include_and_exclude(self):
    return self._make_archive_tester(self).test_create_with_include_and_exclude()

  def xtest_checksum(self):
    return self._make_archive_tester(self).test_checksum()
    
if __name__ == '__main__':
  unit_test.main()
