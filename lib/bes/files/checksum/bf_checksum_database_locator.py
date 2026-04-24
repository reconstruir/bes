#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os
import threading
from os import path

from bes.system.check import check
from bes.system.host import host

class bf_checksum_database_locator:

  _st_dev_cache = {}
  _st_dev_cache_lock = threading.Lock()

  @classmethod
  def database_path_for_file(clazz, filename):
    'Return the path to the SQLite database that should store checksums for filename.'
    check.check_string(filename)

    filename = path.abspath(filename)
    file_dir = path.dirname(filename)
    stat_result = os.stat(file_dir)
    device_id = stat_result.st_dev

    with clazz._st_dev_cache_lock:
      if device_id in clazz._st_dev_cache:
        return clazz._st_dev_cache[device_id]

    database_path = clazz._determine_database_path(filename, device_id)

    with clazz._st_dev_cache_lock:
      clazz._st_dev_cache[device_id] = database_path

    return database_path

  @classmethod
  def _determine_database_path(clazz, filename, device_id):
    volume_root = clazz._find_volume_root(filename)

    if os.access(volume_root, os.W_OK):
      on_volume_path = path.join(volume_root, '.bes_cache', 'checksums.sqlite')
      try:
        os.makedirs(path.dirname(on_volume_path), exist_ok=True)
        return on_volume_path
      except OSError:
        pass

    volume_id = clazz._volume_identifier(volume_root, device_id)
    home_dir = path.expanduser('~/.bes/checksums')
    return path.join(home_dir, f'{volume_id}.sqlite')

  @classmethod
  def _find_volume_root(clazz, filename):
    if host.is_windows():
      drive, _ = path.splitdrive(filename)
      return drive + '\\'

    current = path.dirname(path.abspath(filename))
    current_dev = os.stat(current).st_dev

    while True:
      parent = path.dirname(current)
      if parent == current:
        return current
      parent_dev = os.stat(parent).st_dev
      if parent_dev != current_dev:
        return current
      current = parent
      current_dev = parent_dev

  @classmethod
  def _volume_identifier(clazz, volume_root, device_id):
    return f'{device_id:016x}'

  @classmethod
  def _clear_cache(clazz):
    'Clear the st_dev cache. Intended for testing only.'
    with clazz._st_dev_cache_lock:
      clazz._st_dev_cache.clear()
