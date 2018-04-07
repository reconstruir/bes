#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import sqlite3
import os.path as path
from collections import namedtuple

from bes.common import check
from bes.fs import file_util
from bes.system import log

class sqlite(object):

  # https://stackoverflow.com/questions/16335772/mapping-result-rows-to-namedtuple-in-python-sqlite
  @staticmethod
  def _namedtuple_factory(cursor, row):
    'Returns sqlite rows as named tuples'
    fields = [ col[0] for col in cursor.description ]
    _row_class = namedtuple('_row', fields)
    return _row_class(*row)

  def __init__(self, filename, log_tag = None):
    log.add_logging(self, tag = log_tag or 'sqlite')
    self.log_i('sqlite(filename=%s)' % (filename))
    self._filename = filename
    if self._filename != ':memory:':
      file_util.ensure_file_dir(path.dirname(self._filename))
    self._connection = sqlite3.connect(self._filename)
    self._cursor = self._connection.cursor()

  @property
  def filename(self):
    return self._filename
    
  @property
  def fetch_namedtuples(self):
    return self._connection.row_factory != None
    
  @fetch_namedtuples.setter
  def fetch_namedtuples(self, value):
    check.check_bool(value)
    if value == self.fetch_namedtuples:
      return
    if value:
      self._connection.row_factory = sqlite._namedtuple_factory
    else:
      self._connection.row_factory = None
    self._cursor = self._connection.cursor()
      
  def execute(self, sql, *args, **kwargs):
    self.log_i('execute(%s)' % (sql))
    self._cursor.execute(sql, *args, **kwargs)
   
  def commit(self):
    self.log_i('commit()')
    self._connection.commit()
   
  def executescript(self, sql, *args, **kwargs):
    self.log_i('executescript(%s)' % (sql))
    self._cursor.executescript(sql, *args, **kwargs)

  def has_table(self, table_name):
    check.check_string(table_name)
    sql = """select count(*) from sqlite_master where type='table' and name='{table_name}'""".format(table_name = table_name)
    self._cursor.execute(sql)
    return self._cursor.fetchone()[0] == 1
   
  def ensure_table(self, table_name, table_schema):
    check.check_string(table_name)
    check.check_string(table_schema)
    if self.has_table(table_name):
      return
    self._cursor.execute(table_schema)
    
  def fetchone(self):
    return self._cursor.fetchone()

  def fetchall(self):
    return self._cursor.fetchall()
  
  def select_all(self, sql, *args, **kwargs):
    self.execute(sql, *args, **kwargs)
    return self.fetchall()

  def select_one(self, sql, *args, **kwargs):
    self.execute(sql, *args, **kwargs)
    return self.fetchone()

  def select_namedtuples(self, sql, *args, **kwargs):
    save_fetch_namedtuples = self.fetch_namedtuples
    self.fetch_namedtuples = True
    try:
      self.execute(sql, *args, **kwargs)
      return self.fetchall()
    finally:
      self.fetch_namedtuples = save_fetch_namedtuples
  
