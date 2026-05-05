#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system.check import check

from ..core.bf_volume_locator import bf_volume_locator

class bf_checksum_database_locator:

  @classmethod
  def database_path_for_file(clazz, filename):
    'Return the path to the SQLite database that should store checksums for filename.'
    check.check_string(filename)
    return bf_volume_locator.database_path_for_file(filename, 'checksums', 'checksums.sqlite')

  @classmethod
  def _clear_cache(clazz):
    'Clear the cache. Intended for testing only.'
    bf_volume_locator._clear_cache()
