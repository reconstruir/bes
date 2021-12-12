#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import hashlib
from os import path

from bes.common.json_util import json_util
from bes.fs.file_util import file_util
from bes.system.execute import execute

from .unit_test_description import unit_test_description

class pytest(object):

  @classmethod
  def inspect_file(clazz, filename):
    cache_filename = clazz._cache_filename(filename)
    cache_valid = clazz._cache_is_valid(filename, cache_filename)

    if cache_valid:
      result = clazz._cache_read(cache_filename)
      return [ unit_test_description(*x) for x in result ]
    
    file_util.remove(cache_filename)
    result = clazz._do_inspect_file(filename)
    clazz._cache_write(cache_filename, result, file_util.get_modification_date(filename))
    return result

  @classmethod
  def _do_inspect_file(clazz, filename):
    #print('inspecting: {}'.format(filename))
    cmd = [ 'pytest', '--collect-only', '--quiet', filename ]
    rv = execute.execute(cmd, raise_error = False)
    if rv.exit_code == 2:
      rv.raise_error(log_error = True, print_error = True)
    if rv.exit_code != 0:
      return []
    lines = [ line for line in rv.stdout_lines() if ' collected in ' not in line ]
    result = []
    for line in lines:
      parts = line.split('::')
      fixture = parts[1]
      function = parts[2]
      result.append(unit_test_description(filename, fixture, function))
    return result
  
  @classmethod
  def _hash_filename(clazz, filename):
    hasher = hashlib.new('sha1')
    data = filename.encode('utf-8')
    hasher.update(data)
    return hasher.hexdigest()

  _CACHE_DIR = path.expanduser('~/.bes_test/inspect_cache')
  
  @classmethod
  def _cache_filename(clazz, filename):
    hashed_filename = clazz._hash_filename(filename)
    return path.join(clazz._CACHE_DIR, hashed_filename)

  @classmethod
  def _cache_is_valid(clazz, filename, cache_filename):
    if not path.exists(cache_filename):
      return False
    mtime = file_util.get_modification_date(filename)
    cache_mtime = file_util.get_modification_date(cache_filename)
    mtime = mtime.replace(microsecond = 0)
    return mtime == cache_mtime

  @classmethod
  def _cache_write(clazz, cache_filename, result, mtime):
    file_util.mkdir(clazz._CACHE_DIR)
    json_util.save_file(cache_filename, result, indent = 2, sort_keys = True)
    file_util.set_modification_date(cache_filename, mtime)

  @classmethod
  def _cache_read(clazz, cache_filename):
    return json_util.read_file(cache_filename)
