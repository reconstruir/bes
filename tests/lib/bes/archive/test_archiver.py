#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path
from bes.testing.unit_test import unit_test
from bes.fs import file_util, temp_file
from bes.archive.temp_archive import temp_archive
from bes.archive import archiver, archive_extension

class test_archiver(unit_test):

  def test_find_archives(self):
    tmp_dir = temp_file.make_temp_dir()
    tmp_zip = temp_archive.make_temp_archive([ temp_archive.item('foo.txt', content = 'foo.txt\n') ], archive_extension.ZIP)
    print('tmp_zip: %s' % (str(tmp_zip)))
    tmp_tar = temp_archive.make_temp_archive([ temp_archive.item('foo.txt', content = 'foo.txt\n') ], archive_extension.TAR)
    tmp_tgz = temp_archive.make_temp_archive([ temp_archive.item('foo.txt', content = 'foo.txt\n') ], archive_extension.TGZ)
    tmp_tar_gz = temp_archive.make_temp_archive([ temp_archive.item('foo.txt', content = 'foo.txt\n') ], archive_extension.TAR_GZ)

    file_util.copy(tmp_zip.filename, path.join(tmp_dir, 'archives/zip/tmp_zip.zip'))
    file_util.copy(tmp_tar.filename, path.join(tmp_dir, 'archives/tar/tmp_tar.tar'))
    file_util.copy(tmp_tgz.filename, path.join(tmp_dir, 'archives/tgz/tmp_tgz.tgz'))
    file_util.copy(tmp_tar_gz.filename, path.join(tmp_dir, 'archives/tar_gz/tmp_tar_gz.tar.gz'))
    file_util.save(path.join(tmp_dir, 'archives/zip/fake_zip.zip'), content = 'not a zip\n')
    file_util.save(path.join(tmp_dir, 'archives/tar/fake_tar.tar'), content = 'not a tar\n')
    file_util.save(path.join(tmp_dir, 'archives/tar_gz/fake_tar_gz.tar.gz'), content = 'not a tar.gz\n')

    self.assertEqual( [
      'archives/tar/tmp_tar.tar',
      'archives/tar_gz/tmp_tar_gz.tar.gz',
      'archives/tgz/tmp_tgz.tgz',
      'archives/zip/tmp_zip.zip',
    ], archiver.find_archives(tmp_dir) )
    
if __name__ == '__main__':
  unit_test.main()
