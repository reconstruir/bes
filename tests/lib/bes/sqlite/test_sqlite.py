#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.testing.unit_test import unit_test
from bes.sqlite import sqlite
from bes.fs import temp_file

class test_sqlite(unit_test):

  def test_empty(self):
    db = self._make_tmp_db()
    filename = db.filename
    del db
    self.assertTrue( path.isfile(filename) )

  @classmethod
  def _make_tmp_db(clazz):
    tmp_filename = path.join(temp_file.make_temp_dir(), 'db.sqlite')
    return sqlite(tmp_filename)
    
if __name__ == '__main__':
  unit_test.main()
