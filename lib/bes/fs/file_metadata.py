#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os
import os.path as path
from ..system.check import check
from bes.sqlite.sqlite import sqlite
from bes.fs.file_util import file_util

from ._detail.file_metadata_db import file_metadata_db

class file_metadata(object):
  'Metadata for files using an sql db.'

  DEFAULT_DB_FILENAME = '.bes_file_metadata.db'
  
  def __init__(self, root_dir, db_filename = None):
    check.check_string(root_dir)
    check.check_string(db_filename, allow_none = True)
    self._root_dir = root_dir
    db_filename = db_filename or self.DEFAULT_DB_FILENAME
    if os.sep in db_filename:
      raise ValueError('db_filename should be just a filename not path: {}'.format(db_filename))
    self._db_filename = path.join(self._root_dir, db_filename)
    self._db = file_metadata_db(sqlite(self._db_filename))

  @property
  def db_filename(self):
    return self._db_filename
    
  def get_values(self, what, filename):
    check.check_string(what)
    check.check_string(filename)
    filename = file_util.lstrip_sep(filename)
    return self._db.get_values(what, filename)

  def replace_values(self, what, filename, values):
    check.check_string(what)
    check.check_string(filename)
    filename = file_util.lstrip_sep(filename)
    self._db.replace_values(what, filename, values)

  def set_value(self, what, filename, key, value):
    check.check_string(what)
    check.check_string(filename)
    filename = file_util.lstrip_sep(filename)
    self._db.set_value(what, filename, key, value)

  def get_value(self, what, filename, key):
    check.check_string(what)
    check.check_string(filename)
    filename = file_util.lstrip_sep(filename)
    return self._db.get_value(what, filename, key)

  def clear(self, what, filename):
    check.check_string(what)
    check.check_string(filename)
    filename = file_util.lstrip_sep(filename)
    self._db.clear(what, filename)

  def _table_name(self, what, filename):
    filename = file_util.lstrip_sep(filename)
    return self._db._table_name(what, filename)
