#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from datetime import datetime
from datetime import timezone

from bes.testing.unit_test import unit_test
from bes.sqlite.sqlite import sqlite
from bes.fs.temp_file import temp_file

class test_sqlite(unit_test):

  @classmethod
  def _make_tmp_db(clazz):
    tmp_filename = path.join(temp_file.make_temp_dir(), 'db.sqlite')
    return sqlite(tmp_filename)
  
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

  def test_has_table(self):
    db = self._make_tmp_db()
    db.execute('create table fruits (name text primary key not null, version integer not null)')
    db.commit()
    self.assertEqual( True, db.has_table('fruits') )
    self.assertEqual( False, db.has_table('cheese') )

  def test_has_index(self):
    db = self._make_tmp_db()
    db.execute('create table fruits (name text primary key not null, version integer not null)')
    db.execute('create index fruits_index on fruits(version)')
    db.commit()
    self.assertEqual( True, db.has_index('fruits_index') )
    self.assertEqual( False, db.has_index('cheese_index') )

  def test_has_row(self):
    db = self._make_tmp_db()
    db.execute('''create table fruits (fruit_id integer primary key not null, name text)''')
    db.execute('''insert into fruits (fruit_id, name) values (42, 'kiwi')''')
    db.execute('''insert into fruits (fruit_id, name) values (666, 'lemon')''')
    db.commit()
    
    self.assertEqual( True, db.has_row('fruits', 'fruit_id', 42) )
    self.assertEqual( False, db.has_row('fruits', 'fruit_id', 43) )

    db.execute('''create table people (name text primary key not null, nickname text)''')
    db.execute('''insert into people (name, nickname) values ('Richard', 'dick')''')
    db.execute('''insert into people (name, nickname) values ('Bill', 'bubba')''')
    db.commit()

    self.assertEqual( True, db.has_row('people', 'name', 'Bill') )
    self.assertEqual( False, db.has_row('people', 'name', 'Nunya') )
    
  def test_user_version(self):
    db = self._make_tmp_db()
    self.assertEqual( 0, db.user_version )
    db.user_version = 1
    self.assertEqual( 1, db.user_version )

  def test_date_without_timezone(self):
    schema = r'''
create table something(
  id INTEGER PRIMARY KEY NOT NULL,
  date TIMESTAMP NOT NULL
);
'''
    date = datetime(year = 2022, month = 1, day = 1)
    
    db = self._make_tmp_db()
    db.ensure_table('something', schema)
    db.execute('REPLACE INTO SOMETHING(id, date) VALUES(?, ?)',
               ( 1, datetime(year = 2022, month = 1, day = 1) ))
    self.assertEqual( [
      ( 1, datetime(year = 2022, month = 1, day = 1) ),
    ], db.select_all(f'SELECT * FROM SOMETHING ORDER BY ID') )

  def test_date_with_timezone(self):
    schema = r'''
create table something(
  id INTEGER PRIMARY KEY NOT NULL,
  date TIMESTAMP NOT NULL
);
'''
    date = datetime(year = 2022, month = 1, day = 1)
    
    db = self._make_tmp_db()
    db.ensure_table('something', schema)
    db.execute('REPLACE INTO SOMETHING(id, date) VALUES(?, ?)',
               ( 1, datetime(year = 2022, month = 1, day = 1, tzinfo = timezone.utc) ))
    self.assertEqual( [
      ( 1, datetime(year = 2022, month = 1, day = 1, tzinfo = timezone.utc) ),
    ], db.select_all(f'SELECT * FROM SOMETHING ORDER BY ID') )

  def test_table_version(self):
    schema = r'''
CREATE TABLE something(
  id INTEGER PRIMARY KEY NOT NULL,
  name TEXT NOT NULL
);
'''
    db = self._make_tmp_db()
    db.ensure_table('something', schema)
    self.assertEqual( 0, db.get_table_version('something') )
    db.set_table_version('something', 1)
    self.assertEqual( 1, db.get_table_version('something') )
    
if __name__ == '__main__':
  unit_test.main()
