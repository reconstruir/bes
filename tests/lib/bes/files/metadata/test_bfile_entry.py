#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from datetime import datetime
from datetime import timedelta

from os import path

from bes.files.metadata.bfile_entry import bfile_entry

from bes.fs.file_attributes import file_attributes
from bes.fs.file_attributes_metadata import file_attributes_metadata
from bes.fs.file_mime import file_mime
from bes.fs.file_util import file_util
from bes.fs.file_metadata_getter_base import file_metadata_getter_base
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
    file_util.remove(e.filename)
    self.assertEquals( False, e.exists )

  def test_access(self):
    self.assertEquals( ( True, True, True, False ), self.F().access )

  def test_is_file(self):
    self.assertEquals( True, self.F().is_file )

  def test_is_dir(self):
    self.assertEquals( True, self.D().is_dir )

  def test_size(self):
    self.assertEquals( 3, self.F(content = 'foo').size )
    
  def test_modification_date(self):
    e = self.F()
#    self.assertEquals( 3, self.F(content = 'foo').size )
    
if __name__ == '__main__':
  unit_test.main()
