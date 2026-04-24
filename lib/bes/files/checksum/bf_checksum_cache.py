#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os
import tempfile
import threading
from os import path

from bes.property.cached_class_property import cached_class_property
from bes.system.check import check

from ..attr.bf_attr import bf_attr

from .bf_checksum import bf_checksum
from .bf_checksum_database import bf_checksum_database
from .bf_checksum_database_locator import bf_checksum_database_locator
from .bf_checksum_fingerprint import bf_checksum_fingerprint

class bf_checksum_cache:

  _XATTR_KEY_PREFIX = 'bes__checksum__'
  _XATTR_KEY_SUFFIX = '__0.0'

  _xattr_available_cache = {}
  _xattr_available_cache_lock = threading.Lock()

  _shared_databases = {}
  _shared_databases_lock = threading.Lock()

  @cached_class_property
  def _attr_instance(clazz):
    return bf_attr()

  @classmethod
  def get_checksum(clazz, filename, algorithm):
    'Return cached checksum for filename and algorithm, computing it if needed.'
    check.check_string(filename)
    check.check_string(algorithm)

    filename = path.abspath(filename)

    if clazz._use_xattr_backend(filename):
      xattr_key = clazz._xattr_key(algorithm)
      value_maker = lambda f: bf_checksum.checksum(f, algorithm).encode('utf-8')
      result_bytes = clazz._attr_instance.get_cached_bytes(filename, xattr_key, value_maker)
      return result_bytes.decode('utf-8')

    fingerprint_key = bf_checksum_fingerprint.make_key(filename)
    database = clazz._get_database(filename)
    cached = database.get_checksum(fingerprint_key, algorithm)
    if cached is not None:
      return cached

    checksum = bf_checksum.checksum(filename, algorithm)
    database.set_checksum(fingerprint_key, bf_checksum_fingerprint.VERSION, algorithm, checksum)
    return checksum

  @classmethod
  def has_cached(clazz, filename, algorithm):
    'Return True if a fresh cached checksum exists without computing it.'
    check.check_string(filename)
    check.check_string(algorithm)

    filename = path.abspath(filename)

    if clazz._use_xattr_backend(filename):
      xattr_key = clazz._xattr_key(algorithm)
      result = clazz._attr_instance.get_cached_bytes_if_fresh(filename, xattr_key)
      return result is not None

    if not path.exists(filename):
      return False
    fingerprint_key = bf_checksum_fingerprint.make_key(filename)
    database = clazz._get_database(filename)
    return database.get_checksum(fingerprint_key, algorithm) is not None

  @classmethod
  def invalidate(clazz, filename, algorithm=None):
    'Remove cached checksum(s) for filename. If algorithm is None, remove all.'
    check.check_string(filename)
    check.check_string(algorithm, allow_none=True)

    abs_filename = path.abspath(filename)

    if path.exists(abs_filename) and os.access(abs_filename, os.W_OK):
      stat_result = os.stat(abs_filename)
      device_id = stat_result.st_dev
      if clazz._xattr_is_available(abs_filename, device_id):
        if algorithm is not None:
          xattr_key = clazz._xattr_key(algorithm)
          clazz._attr_instance.remove_mtime_key(abs_filename, xattr_key)
          if clazz._attr_instance.has_key(abs_filename, xattr_key):
            clazz._attr_instance.remove(abs_filename, xattr_key)
        else:
          from .bf_checksum_algorithm import bf_checksum_algorithm
          for alg in bf_checksum_algorithm.ALL:
            xattr_key = clazz._xattr_key(alg)
            clazz._attr_instance.remove_mtime_key(abs_filename, xattr_key)
            if clazz._attr_instance.has_key(abs_filename, xattr_key):
              clazz._attr_instance.remove(abs_filename, xattr_key)

    if path.exists(abs_filename):
      try:
        fingerprint_key = bf_checksum_fingerprint.make_key(abs_filename)
        database = clazz._get_database(abs_filename)
        database.delete_checksum(fingerprint_key, algorithm)
      except Exception:
        pass

  @classmethod
  def _use_xattr_backend(clazz, filename):
    if not os.access(filename, os.W_OK):
      return False
    stat_result = os.stat(filename)
    return clazz._xattr_is_available(filename, stat_result.st_dev)

  @classmethod
  def _xattr_is_available(clazz, filename, device_id):
    with clazz._xattr_available_cache_lock:
      if device_id in clazz._xattr_available_cache:
        return clazz._xattr_available_cache[device_id]

    result = clazz._probe_xattr_available(filename)

    with clazz._xattr_available_cache_lock:
      clazz._xattr_available_cache[device_id] = result

    return result

  @classmethod
  def _probe_xattr_available(clazz, filename):
    dirname = path.dirname(path.abspath(filename))
    tmp_path = None
    try:
      tmp_fd, tmp_path = tempfile.mkstemp(dir=dirname, prefix='.bes_probe_')
      os.close(tmp_fd)
      probe_key = 'bes_probe'
      probe_value = b'1'
      clazz._attr_instance.set_bytes(tmp_path, probe_key, probe_value)
      result = clazz._attr_instance.get_bytes(tmp_path, probe_key)
      clazz._attr_instance.remove(tmp_path, probe_key)
      return result == probe_value
    except Exception:
      return False
    finally:
      if tmp_path is not None:
        try:
          os.unlink(tmp_path)
        except Exception:
          pass

  @classmethod
  def _xattr_key(clazz, algorithm):
    return f'{clazz._XATTR_KEY_PREFIX}{algorithm}{clazz._XATTR_KEY_SUFFIX}'

  @classmethod
  def _get_database(clazz, filename):
    database_path = bf_checksum_database_locator.database_path_for_file(filename)
    with clazz._shared_databases_lock:
      if database_path not in clazz._shared_databases:
        clazz._shared_databases[database_path] = bf_checksum_database(database_path)
      return clazz._shared_databases[database_path]
