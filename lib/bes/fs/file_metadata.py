#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.common.check import check
from bes.sqlite.sqlite import sqlite

from .detail.file_metadata_db import file_metadata_db

class file_metadata(object):
  'Metadata for files using an sql db.'
  
  def __init__(self, db_filename):
    self._db_filename = db_filename
    self._db = file_metadata_db(sqlite(self._db_filename))
    
  def get_values(self, filename):
    return self._db.get_values(filename)

  def replace_values(self, filename, values):
    self._db.replace_values(filename, values)

  def set_value(self, filename, key, value):
    self._db.set_value(filename, key, value)

  def get_value(self, filename, key):
    return self._db.get_value(filename, key)

  def clear(self, filename):
    self._db.clear(filename)
