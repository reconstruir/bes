#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from datetime import datetime
from datetime import timedelta

from os import path

from bes.files.bfile_entry import bfile_entry
from bes.system.filesystem import filesystem

from bes.system.filesystem import filesystem
from bes.system.host import host
from bes.testing.unit_test import unit_test

from _bes_unit_test_common.unit_test_media import unit_test_media
from _bes_unit_test_common.unit_test_media_files import unit_test_media_files

class test_bfile_entry(unit_test, unit_test_media_files):

  def F(self, *args, **kargs):
    tmp = self.make_temp_file(*args, **kargs)
    return bfile_entry(tmp)

  def D(self, *args, **kargs):
    tmp = self.make_temp_dir(*args, **kargs)
    return bfile_entry(tmp)
  
  def test_exits_true(self):
    self.assertEquals( True, self.F().exists )

  def test_exits_false(self):
    e = self.F()
    self.assertEquals( True, e.exists )
    filesystem.remove(e.filename)
    self.assertEquals( False, e.exists )

  def test_access(self):
    self.assertEquals( ( True, True, True, False ), self.F().access )

  def test_is_file(self):
    self.assertEquals( True, self.F().is_file )

  def test_is_dir(self):
    self.assertEquals( True, self.D().is_dir )

  def test_size(self):
    self.assertEquals( 4, self.F(content = 'kiwi').size )

  def test_extension(self):
    self.assertEquals( 'kiwi', self.F(suffix = '.kiwi').extension )
    
  def test_modification_date_get(self):
    e = self.F()
    self.assertEqual( datetime.fromtimestamp(path.getmtime(e.filename)), e.modification_date )

  def test_modification_date_set(self):
    e = self.F()
    d = datetime(year = 2000, month = 1, day = 1, hour = 1, second = 1)
    e.modification_date = d
    self.assertEqual( d, e.modification_date )

  def test_modification_date_timestamp(self):
    e = self.F()
    e.modification_date = datetime(year = 2000, month = 1, day = 1, hour = 1, second = 1)
    self.assertEqual( '2000-01-01-01-00-01', e.modification_date_timestamp )

if __name__ == '__main__':
  unit_test.main()