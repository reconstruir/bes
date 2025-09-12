#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os
import hashlib

from os import path

from bes.system.check import check
from bes.system.log import logger
from bes.sqlite.sqlite import sqlite

from ..bf_check import bf_check
#from .bf_checksum import bf_checksum

from .bf_hasher_base import bf_hasher_base
from .bf_hasher_hashlib import bf_hasher_hashlib

class bf_hasher_cached_sqlite(bf_hasher_base):

  log = logger('bf_hasher')
  
  _CHECKSUMS_SCHEMA_TEMPLATE_V1 = '''
create table {table_name}(
    hash_key TEXT PRIMARY KEY NOT NULL,
    checksum TEXT NOT NULL
);
'''

  def __init__(self, db_filename):
    check.check_string(db_filename)
    
    self._db_filename = db_filename
    self._db = sqlite(self._db_filename)
    self._ensure_checksums_table('checksums_sha256_v1')
    self._ensure_checksums_table('short_checksums_sha256_v1')
    self._num_computations = 0
    self._hasher = bf_hasher_hashlib()

  def _ensure_checksums_table(self, table_name):
    schema = self._CHECKSUMS_SCHEMA_TEMPLATE_V1.format(table_name = table_name)
    self._db.ensure_table(table_name, schema)
    
  #@abc.abstractmethod
  def checksum_sha(self, filename, algorithm, chunk_size, num_chunks):
    """Return checksum for filename using sha algorithm."""
    filename = bf_check.check_file(filename)
    check.check_string(algorithm)
    
    table_name = f'checksums_{algorithm}_v1'
    return self._do_checksum_sha(filename, table_name, algorithm, chunk_size, num_chunks)

  #@abc.abstractmethod
  def checksum_short_sha(self, filename, algorithm):
    """Return a short checksum for filename using sha algorithm."""
    filename = bf_check.check_file(filename)
    check.check_string(algorithm)

    table_name = f'short_checksums_{algorithm}_v1'
    return self._do_checksum_sha(filename, table_name, algorithm, chunk_size, num_chunks)

  def _do_checksum_sha(self, filename, table_name, algorithm, chunk_size, num_chunks):
    hash_key = self._make_hash_key(filename)
    rows = self._db.select_all(f'SELECT checksum FROM {table_name} WHERE hash_key=?',
                               ( hash_key, ))
    if not rows:
      checksum = self._hasher.checksum_sha(filename,
                                           algorithm,
                                           chunk_size = chunk_size,
                                           num_chunks = num_chunks)
      self._num_computations += 1      
      self._db.execute(f'INSERT INTO {table_name}(hash_key, checksum) VALUES(?, ?)',
                       ( hash_key, checksum, ))
    else:
      assert len(rows) == 1
      checksum = rows[0][0]
    return checksum
  
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
    if not rows:
      checksum_sha256 = bf_checksum.checksum(filename, 'sha256')
      self._num_computations += 1      
      self._db.execute('INSERT INTO checksums_v1(hash_key, checksum_sha256) VALUES(?, ?)',
                       ( hash_key, checksum_sha256, ))
    else:
      assert len(rows) == 1
      checksum_sha256 = rows[0][0]
    return checksum_sha256

  def _checksum_sha_from_db(self, filename):
    hash_key = self._make_hash_key(filename)
    rows = self._db.select_all('SELECT checksum_sha256 FROM checksums_v1 WHERE hash_key=?',
                              ( hash_key, ))
    if not rows:
      return None
    else:
      assert len(rows) == 1
      checksum_sha256 = rows[0][0]
    return checksum_sha256
  
