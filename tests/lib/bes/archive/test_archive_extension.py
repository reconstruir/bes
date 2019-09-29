#!/usr/bin/env python3
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.archive.archive_extension import archive_extension

class test_archive_extension(unit_test):

  def test_write_format(self):
    self.assertEqual( 'w:gz', archive_extension.write_format('gz') )
    self.assertEqual( 'w:gz', archive_extension.write_format('tgz') )
    self.assertEqual( 'w:gz', archive_extension.write_format('tar.gz') )
    self.assertEqual( 'w', archive_extension.write_format('tar') )
    self.assertEqual( 'w:bz2', archive_extension.write_format('tar.bz2') )
    self.assertEqual( 'w:bz2', archive_extension.write_format('bz2') )
    self.assertEqual( 'w', archive_extension.write_format('zip') )

  def test_write_format_for_filename(self):
    self.assertEqual( 'w:gz', archive_extension.write_format_for_filename('foo.gz') )
    self.assertEqual( 'w:gz', archive_extension.write_format_for_filename('foo.tgz') )
    self.assertEqual( 'w:gz', archive_extension.write_format_for_filename('foo.tar.gz') )
    self.assertEqual( 'w', archive_extension.write_format_for_filename('foo.tar') )
    self.assertEqual( 'w:bz2', archive_extension.write_format_for_filename('foo.tar.bz2') )
    self.assertEqual( 'w:bz2', archive_extension.write_format_for_filename('foo.bz2') )
    self.assertEqual( 'w', archive_extension.write_format_for_filename('foo.zip') )

  def test_extension_for_filename(self):
    self.assertEqual( 'tar.gz', archive_extension.extension_for_filename('foo.tar.gz') )
    self.assertEqual( 'gz', archive_extension.extension_for_filename('foo.gz') )
    self.assertEqual( 'zip', archive_extension.extension_for_filename('foo.zip') )
    self.assertEqual( 'tgz', archive_extension.extension_for_filename('foo.tgz') )
    self.assertEqual( 'bz2', archive_extension.extension_for_filename('foo.bz2') )
    self.assertEqual( 'tar.bz2', archive_extension.extension_for_filename('foo.tar.bz2') )
    self.assertEqual( 'dmg', archive_extension.extension_for_filename('foo.dmg') )
    self.assertEqual( 'xz', archive_extension.extension_for_filename('foo.xz') )
    self.assertEqual( None, archive_extension.extension_for_filename('foo.7zip') )

if __name__ == "__main__":
  unit_test.main()
