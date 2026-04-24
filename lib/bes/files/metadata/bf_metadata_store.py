#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system.check import check

from .bf_metadata_database import bf_metadata_database
from .bf_metadata_database_locator import bf_metadata_database_locator

class bf_metadata_store:

  def __init__(self, database_path = None):
    check.check_string(database_path, allow_none = True)

    resolved_path = database_path or bf_metadata_database_locator.default_database_path()
    self._database = bf_metadata_database(resolved_path)

  def get(self, checksum, key):
    check.check_string(checksum)
    check.check_string(key)

    return self._database.get(checksum, key)

  def set(self, checksum, key, value):
    check.check_string(checksum)
    check.check_string(key)
    check.check_string(value)

    self._database.set(checksum, key, value)

  def delete(self, checksum, key = None):
    check.check_string(checksum)
    check.check_string(key, allow_none = True)

    self._database.delete(checksum, key)

  def keys(self, checksum):
    check.check_string(checksum)

    return self._database.keys(checksum)

  def get_all(self, checksum):
    check.check_string(checksum)

    return self._database.get_all(checksum)
