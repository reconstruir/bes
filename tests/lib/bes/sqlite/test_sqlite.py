#!/usr/bin/env python3
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.testing.unit_test import unit_test
from bes.sqlite.sqlite import sqlite
from bes.fs.temp_file import temp_file

class test_sqlite(unit_test):

  def test_empty(self):
    db = self._make_tmp_db()
    filename = db.filename
    del db
    self.assertTrue( path.isfile(filename) )

  def test_fetch_namedtuples(self):
    db = self._make_tmp_db()

    db.execute('''create table fruits (name text primary key not null, version integer not null)''')
    db.execute('''insert into fruits (name, version) values ('kiwi', '1.2.3')''')
    db.execute('''insert into fruits (name, version) values ('apple', '2.3.4')''')
    db.commit()
    
    actual = db.select_all('''select * from fruits''')
    expected = [
      ( 'kiwi', '1.2.3' ),
      ( 'apple', '2.3.4' ),
    ]
    self.assertTrue( type(actual[0]) == tuple )
    self.assertTrue( type(actual[1]) == tuple )
    self.assertTrue( expected, actual )

    db.fetch_namedtuples = True

    actual = db.select_all('''select * from fruits''')
    self.assertTrue( type(actual[0]) != tuple )
    self.assertTrue( type(actual[1]) != tuple )
    self.assertEqual( 'kiwi', actual[0].name )
    self.assertEqual( '1.2.3', actual[0].version )
    self.assertEqual( 'apple', actual[1].name )
    self.assertEqual( '2.3.4', actual[1].version )

    db.fetch_namedtuples = False
    
    actual = db.select_all('''select * from fruits''')
    expected = [
      ( 'kiwi', '1.2.3' ),
      ( 'apple', '2.3.4' ),
    ]
    self.assertTrue( type(actual[0]) == tuple )
    self.assertTrue( type(actual[1]) == tuple )
    self.assertTrue( expected, actual )
    
  @classmethod
  def _make_tmp_db(clazz):
    tmp_filename = path.join(temp_file.make_temp_dir(), 'db.sqlite')
    return sqlite(tmp_filename)
    
if __name__ == '__main__':
  unit_test.main()
