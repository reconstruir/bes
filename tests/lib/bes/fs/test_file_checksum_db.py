#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import time
from bes.testing.unit_test import unit_test
import os, os.path as path, tempfile
from bes.fs.file_checksum_db import file_checksum_db
from bes.fs.file_util import file_util
from bes.fs.temp_file import temp_file

class test_file_metadata_db(unit_test):

  def test_file_first_time(self):
    tmp_db = temp_file.make_temp_file(suffix = '.sqlite.db')
    db = file_checksum_db(tmp_db)
    tmp_file = temp_file.make_temp_file(suffix = '.txt', content = 'this is foo\n')
    self.assertEqual( 0, db.count )
    self.assertEqual( file_util.checksum('sha256', tmp_file), db.checksum('sha256', tmp_file) )
    self.assertEqual( 1, db.count )
    self.assertEqual( file_util.checksum('sha256', tmp_file), db.checksum('sha256', tmp_file) )
    self.assertEqual( 1, db.count )
    
  def test_file_persistence(self):
    tmp_db = temp_file.make_temp_file(suffix = '.sqlite.db')
    db = file_checksum_db(tmp_db)
    tmp_file = temp_file.make_temp_file(suffix = '.txt', content = 'this is foo\n')
    self.assertEqual( 0, db.count )
    self.assertEqual( file_util.checksum('sha256', tmp_file), db.checksum('sha256', tmp_file) )
    self.assertEqual( 1, db.count )
    db = file_checksum_db(tmp_db)
    self.assertEqual( file_util.checksum('sha256', tmp_file), db.checksum('sha256', tmp_file) )
    self.assertEqual( 0, db.count )
    
  def test_file_changed(self):
    tmp_db = temp_file.make_temp_file(suffix = '.sqlite.db')
    db = file_checksum_db(tmp_db)
    tmp_file = temp_file.make_temp_file(suffix = '.txt', content = 'this is foo\n')
    self.assertEqual( 0, db.count )
    self.assertEqual( file_util.checksum('sha256', tmp_file), db.checksum('sha256', tmp_file) )
    self.assertEqual( 1, db.count )
    time.sleep(0.100) # need to sleep to let the mtime change
    with open(tmp_file, 'a') as fout:
      fout.write('changed')
      fout.flush()
    self.assertEqual( file_util.checksum('sha256', tmp_file), db.checksum('sha256', tmp_file) )
    self.assertEqual( 2, db.count )
    self.assertEqual( file_util.checksum('sha256', tmp_file), db.checksum('sha256', tmp_file) )
    self.assertEqual( 2, db.count )
    
if __name__ == '__main__':
  unit_test.main()
