#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from bes.system.check import check

from ..checksum.bf_checksum_cache import bf_checksum_cache

from .bf_metadata_store import bf_metadata_store

class bf_metadata_file_store:

  def __init__(self, database_path = None):
    check.check_string(database_path, allow_none = True)

    self._store = bf_metadata_store(database_path = database_path)

  def get(self, filename, key):
    check.check_string(filename)
    check.check_string(key)

    checksum = bf_checksum_cache.get_checksum(path.abspath(filename), 'sha256')
    return self._store.get(checksum, key)

  def set(self, filename, key, value):
    check.check_string(filename)
    check.check_string(key)
    check.check_string(value)

    checksum = bf_checksum_cache.get_checksum(path.abspath(filename), 'sha256')
    self._store.set(checksum, key, value)

  def delete(self, filename, key = None):
    check.check_string(filename)
    check.check_string(key, allow_none = True)

    checksum = bf_checksum_cache.get_checksum(path.abspath(filename), 'sha256')
    self._store.delete(checksum, key)

  def keys(self, filename):
    check.check_string(filename)

    checksum = bf_checksum_cache.get_checksum(path.abspath(filename), 'sha256')
    return self._store.keys(checksum)

  def get_all(self, filename):
    check.check_string(filename)

    checksum = bf_checksum_cache.get_checksum(path.abspath(filename), 'sha256')
    return self._store.get_all(checksum)
