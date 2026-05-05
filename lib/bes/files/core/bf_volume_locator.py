#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os
import threading
from os import path

from bes.system.check import check
from bes.system.host import host

class bf_volume_locator:
  'Find a writable directory on the same device as a given file.'

  _cache = {}
  _cache_lock = threading.Lock()

  @classmethod
  def directory_for_file(clazz, filename, purpose):
    'Return a writable directory on the same device as filename, scoped by purpose.'
    check.check_string(filename)
    check.check_string(purpose)

    filename = path.abspath(filename)
    lookup_dir = filename if path.isdir(filename) else path.dirname(filename)
    device_id = os.stat(lookup_dir).st_dev

    cache_key = (device_id, purpose)
    with clazz._cache_lock:
      if cache_key in clazz._cache:
        return clazz._cache[cache_key]

    result = clazz._determine_directory(filename, device_id, purpose)

    with clazz._cache_lock:
      clazz._cache[cache_key] = result

    return result

  @classmethod
  def database_path_for_file(clazz, filename, purpose, db_name):
    'Return a path for a SQLite database on the same device as filename.'
    check.check_string(filename)
    check.check_string(purpose)
    check.check_string(db_name)

    directory = clazz.directory_for_file(filename, purpose)
    return path.join(directory, db_name)

  @classmethod
  def _determine_directory(clazz, filename, device_id, purpose):
    volume_root = clazz._find_volume_root(filename)

    if os.access(volume_root, os.W_OK):
      candidate = path.join(volume_root, '.bes_cache', purpose)
      try:
        os.makedirs(candidate, exist_ok=True)
        return candidate
      except OSError:
        pass

    volume_id = clazz._volume_identifier(volume_root, device_id)
    fallback = path.expanduser(path.join('~', '.bes', purpose, volume_id))
    os.makedirs(fallback, exist_ok=True)
    return fallback

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
    'Clear the device cache. Intended for testing only.'
    with clazz._cache_lock:
      clazz._cache.clear()
