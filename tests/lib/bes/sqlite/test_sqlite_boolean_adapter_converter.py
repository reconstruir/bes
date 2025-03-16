#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from datetime import datetime
from datetime import timezone

from bes.testing.unit_test import unit_test
from bes.sqlite.sqlite import sqlite
from bes.fs.temp_file import temp_file

class test_sqlite_boolean_adapter_converter(unit_test):

  @classmethod
  def _make_tmp_db(clazz):
    tmp_filename = path.join(temp_file.make_temp_dir(), 'db.sqlite')
    return sqlite(tmp_filename)

  def test_boolean(self):
    schema = r'''
create table something(
  id INTEGER PRIMARY KEY NOT NULL,
  is_happy BOOLEAN NOT NULL
);
'''
    db = self._make_tmp_db()
    db.ensure_table('something', schema)
    db.execute('REPLACE INTO SOMETHING(id, is_happy) VALUES(?, ?)',
               ( 1, True ))
    self.assertEqual( [
      ( 1, True ),
    ], db.select_all(f'SELECT * FROM SOMETHING ORDER BY ID') )
    
if __name__ == '__main__':
  unit_test.main()
