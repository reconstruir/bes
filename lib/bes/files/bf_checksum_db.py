#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os
import hashlib

from os import path

from bes.system.check import check
from bes.system.log import logger
from bes.sqlite.sqlite import sqlite

from .bf_check import bf_check
from .bf_checksum import bf_checksum

class bf_checksum_db(object):

  log = logger('bf_checksum')
  
  _CHECKSUMS_V1_TABLE_SCHEMA = r'''
create table checksums_v1(
    hash_key TEXT PRIMARY KEY NOT NULL,
    checksum_sha256 TEXT NOT NULL
);
'''

  def __init__(self, db_filename):
    check.check_string(db_filename)
    
    self._db_filename = db_filename
    self._db = sqlite(self._db_filename)
    self._db.ensure_table('checksums_v1', self._CHECKSUMS_V1_TABLE_SCHEMA)
    self._num_computations = 0

  @property
  def num_computations(self):
    return self._num_computations
  
  @classmethod
  def _make_hash_key(clazz, filename):
    assert path.isabs(filename)
    stat = os.stat(filename)
    mtime = int(stat.st_mtime)
    size = stat.st_size
    hash_string = f'{mtime}_{size}_{filename}'
    hash_object = hashlib.sha256(hash_string.encode('utf-8'))
    return hash_object.hexdigest()
    
  def get_checksum(self, filename):
    filename = bf_check.check_file(filename)

    hash_key = self._make_hash_key(filename)
    rows = self._db.select_all('SELECT checksum_sha256 FROM checksums_v1 WHERE hash_key=?',
                              ( hash_key, ))
    #print(rows)
    if not rows:
      checksum_sha256 = bf_checksum.checksum(filename, 'sha256')
      self._num_computations += 1      
      self._db.execute('INSERT INTO checksums_v1(hash_key, checksum_sha256) values(?, ?)',
                       ( hash_key, checksum_sha256, ))
    else:
      assert len(rows) == 1
      checksum_sha256 = rows[0][0]
    return checksum_sha256
