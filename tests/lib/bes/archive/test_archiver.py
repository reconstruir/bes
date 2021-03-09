#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path
from bes.testing.unit_test import unit_test
from bes.fs.file_util import file_util
from bes.fs.temp_file import temp_file
from bes.archive.temp_archive import temp_archive
from bes.archive.archiver import archiver
from bes.archive.archive_extension import archive_extension
from bes.fs.testing.temp_content import temp_content

class test_archiver(unit_test):

  def test_find_archives(self):
    tmp_dir = temp_file.make_temp_dir()
    tmp_zip = temp_archive.make_temp_archive([ temp_archive.item('foo.txt', content = 'foo.txt\n') ], archive_extension.ZIP)
    tmp_tar = temp_archive.make_temp_archive([ temp_archive.item('foo.txt', content = 'foo.txt\n') ], archive_extension.TAR)
    tmp_tgz = temp_archive.make_temp_archive([ temp_archive.item('foo.txt', content = 'foo.txt\n') ], archive_extension.TGZ)
    tmp_tar_gz = temp_archive.make_temp_archive([ temp_archive.item('foo.txt', content = 'foo.txt\n') ], archive_extension.TAR_GZ)

    file_util.copy(tmp_zip, path.join(tmp_dir, 'archives/zip/tmp_zip.zip'))
    file_util.copy(tmp_tar, path.join(tmp_dir, 'archives/tar/tmp_tar.tar'))
    file_util.copy(tmp_tgz, path.join(tmp_dir, 'archives/tgz/tmp_tgz.tgz'))
    file_util.copy(tmp_tar_gz, path.join(tmp_dir, 'archives/tar_gz/tmp_tar_gz.tar.gz'))
    file_util.save(path.join(tmp_dir, 'archives/zip/fake_zip.zip'), content = 'not a zip\n')
    file_util.save(path.join(tmp_dir, 'archives/tar/fake_tar.tar'), content = 'not a tar\n')
    file_util.save(path.join(tmp_dir, 'archives/tar_gz/fake_tar_gz.tar.gz'), content = 'not a tar.gz\n')

    self.assertEqual( [
      self.p('archives/tar/tmp_tar.tar'),
      self.p('archives/tar_gz/tmp_tar_gz.tar.gz'),
      self.p('archives/tgz/tmp_tgz.tgz'),
      self.p('archives/zip/tmp_zip.zip'),
    ], archiver.find_archives(tmp_dir) )

  def test_create_tar_gz(self):
    tmp_dir = temp_content.write_items_to_temp_dir([
        'file a/b/c/foo.txt "foo content" 755',
        'file d/e/bar.txt "bar content" 644',
        'dir  baz     ""            700',
    ])
    tmp_archive = self.make_temp_file(suffix = '.tar.gz')
    archiver.create(tmp_archive, tmp_dir)
    self.assertEqual( [
      'a/b/c/foo.txt',
      'd/e/bar.txt',
    ], archiver.members(tmp_archive) )
    self.assertEqual( 'tgz', archiver.format_name(tmp_archive) )

  def test_create_tar(self):
    tmp_dir = temp_content.write_items_to_temp_dir([
        'file a/b/c/foo.txt "foo content" 755',
        'file d/e/bar.txt "bar content" 644',
        'dir  baz     ""            700',
    ])
    tmp_archive = self.make_temp_file(suffix = '.tar')
    archiver.create(tmp_archive, tmp_dir)
    self.assertEqual( [
      'a/b/c/foo.txt',
      'd/e/bar.txt',
    ], archiver.members(tmp_archive) )
    self.assertEqual( 'tar', archiver.format_name(tmp_archive) )
    
  def test_create_tgz(self):
    tmp_dir = temp_content.write_items_to_temp_dir([
        'file a/b/c/foo.txt "foo content" 755',
        'file d/e/bar.txt "bar content" 644',
        'dir  baz     ""            700',
    ])
    tmp_archive = self.make_temp_file(suffix = '.tgz')
    archiver.create(tmp_archive, tmp_dir)
    self.assertEqual( [
      'a/b/c/foo.txt',
      'd/e/bar.txt',
    ], archiver.members(tmp_archive) )
    self.assertEqual( 'tgz', archiver.format_name(tmp_archive) )
    
  def test_create_zip(self):
    tmp_dir = temp_content.write_items_to_temp_dir([
        'file a/b/c/foo.txt "foo content" 755',
        'file d/e/bar.txt "bar content" 644',
        'dir  baz     ""            700',
    ])
    tmp_archive = self.make_temp_file(suffix = '.zip')
    archiver.create(tmp_archive, tmp_dir)
    self.assertEqual( [
      'a/b/c/foo.txt',
      'd/e/bar.txt',
    ], archiver.members(tmp_archive) )
    self.assertEqual( 'zip', archiver.format_name(tmp_archive) )

  def test_create_force_tar_gz(self):
    tmp_dir = temp_content.write_items_to_temp_dir([
        'file a/b/c/foo.txt "foo content" 755',
        'file d/e/bar.txt "bar content" 644',
        'dir  baz     ""            700',
    ])
    tmp_archive = self.make_temp_file()
    archiver.create(tmp_archive, tmp_dir, extension = 'tar.gz')
    self.assertEqual( [
      'a/b/c/foo.txt',
      'd/e/bar.txt',
    ], archiver.members(tmp_archive) )
    self.assertEqual( 'tgz', archiver.format_name(tmp_archive) )

  def test_create_force_zip(self):
    tmp_dir = temp_content.write_items_to_temp_dir([
        'file a/b/c/foo.txt "foo content" 755',
        'file d/e/bar.txt "bar content" 644',
        'dir  baz     ""            700',
    ])
    tmp_archive = self.make_temp_file()
    archiver.create(tmp_archive, tmp_dir, extension = 'zip')
    self.assertEqual( [
      'a/b/c/foo.txt',
      'd/e/bar.txt',
    ], archiver.members(tmp_archive) )
    self.assertEqual( 'zip', archiver.format_name(tmp_archive) )

  def test_filenames_with_brackets_zip(self):
    tmp_dir = temp_content.write_items_to_temp_dir([
        'file .foo/bar-[baz].ext-kiwi.apple.lemon "something" 644',
    ], delete = not self.DEBUG)
    tmp_archive = self.make_temp_file()
    archiver.create(tmp_archive, tmp_dir, extension = 'zip')
    self.assertEqual( [
      '.foo/bar-[baz].ext-kiwi.apple.lemon',
    ], archiver.members(tmp_archive) )
    self.assertEqual( 'zip', archiver.format_name(tmp_archive) )
    self.assertEqual( '3fc9b689459d738f8c88a3a48aa9e33542016b7a4052e001aaa536fca74813cb',
                      archiver.member_checksum(tmp_archive, '.foo/bar-[baz].ext-kiwi.apple.lemon') )
    
  def test_filenames_with_brackets_tar(self):
    tmp_dir = temp_content.write_items_to_temp_dir([
        'file .foo/bar-[baz].ext-kiwi.apple.lemon "something" 644',
    ], delete = not self.DEBUG)
    tmp_archive = self.make_temp_file()
    archiver.create(tmp_archive, tmp_dir, extension = 'tar.gz')
    self.assertEqual( [
      '.foo/bar-[baz].ext-kiwi.apple.lemon',
    ], archiver.members(tmp_archive) )
    self.assertEqual( 'tgz', archiver.format_name(tmp_archive) )
    self.assertEqual( '3fc9b689459d738f8c88a3a48aa9e33542016b7a4052e001aaa536fca74813cb',
                      archiver.member_checksum(tmp_archive, '.foo/bar-[baz].ext-kiwi.apple.lemon') )
    
  def test_transform(self):
    tmp_dir = temp_content.write_items_to_temp_dir([
        'file files/foo.txt "this is foo.txt" 644',
        'file files/bar.txt "this is bar.txt" 644',
        'file files/baz.txt "this is baz.txt" 644',
    ], delete = not self.DEBUG)
    tmp_archive = self.make_temp_file(suffix = '.zip')
    archiver.create(tmp_archive, tmp_dir)

    from bes.archive.archive_operation_add_file import archive_operation_add_file
    from bes.archive.archive_operation_remove_files import archive_operation_remove_files
    operations = [
      archive_operation_add_file('new/new_file.txt', 'this is new_file.txt', 0o0644),
      archive_operation_remove_files([ 'files/foo.txt', 'files/bar.txt' ]),
    ]
    archiver.transform(tmp_archive, operations)
    self.assertEqual( [
      'files/baz.txt',
      'new/new_file.txt',
    ], archiver.members(tmp_archive) )
    self.assertEqual( 'this is new_file.txt', archiver.extract_member_to_string(tmp_archive, 'new/new_file.txt', codec = 'utf8') )

  def test_create_with_exclude(self):
    tmp_dir = temp_content.write_items_to_temp_dir([
        'file a/b/c/foo.txt "foo content" 755',
        'file d/e/bar.txt "bar content" 644',
        'dir  baz     ""            700',
    ])
    tmp_archive = self.make_temp_file(suffix = '.zip')
    archiver.create(tmp_archive, tmp_dir, exclude = [ self.xp_path('d/e/bar.txt') ] )
    self.assertEqual( [
      'a/b/c/foo.txt',
    ], archiver.members(tmp_archive) )
    
if __name__ == '__main__':
  unit_test.main()
