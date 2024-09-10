#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from multiprocessing import Lock
from abc import abstractmethod, ABCMeta
from collections import namedtuple
import sys

from bes.system.host import host
from bes.text.line_break import line_break
from bes.system.log import logger

from .file_util import file_util
from .temp_file import temp_file

cache_info = namedtuple('cache_info', 'cached_filename, checksum_filename, cached_checksum')

class file_cache_item_base(object, metaclass = ABCMeta):

  @abstractmethod
  def __init__(self):
    pass

  @abstractmethod
  def save(self, info):
    assert False, 'not implemented'

  @abstractmethod
  def load(self, cached_filename):
    assert False, 'not implemented'

  @abstractmethod
  def name(self):
    assert False, 'not implemented'

  @abstractmethod
  def checksum(self):
    assert False, 'not implemented'

class file_cache_item(file_cache_item_base):

  _log = logger('file_cache')
  
  def __init__(self, filename):
    super(file_cache_item, self).__init__()
    self.filename = path.abspath(path.normpath(filename))
    self._checksum = file_util.checksum('sha256', self.filename)
    self._log.log_d('file_cache_item:__init__: filename={} checksum={}'.format(self.filename,
                                                                               self._checksum))
    
  def __str__(self):
    return '{}:{}'.format(self.filename, self._checksum)
  
  def save(self, info):
    assert path.isfile(self.filename)
    self._log.log_d('file_cache_item:save: filename={} info={}'.format(self.filename, info))
    file_util.copy(self.filename, info.cached_filename)
    file_util.save(info.checksum_filename, self._checksum + line_break.DEFAULT_LINE_BREAK)

  def checksum(self):
    return self._checksum

  def name(self):
    return self.filename

class file_filename_cache_item(file_cache_item):
  def __init__(self, filename):
    super(file_filename_cache_item, self).__init__(filename)

  def load(self, cached_filename):
    assert path.isfile(cached_filename)
    tmp_copy = temp_file.make_temp_file(prefix = 'cached_')
    file_util.copy(cached_filename, tmp_copy)
    return tmp_copy

class file_content_cache_item(file_cache_item):
  def __init__(self, filename):
    super(file_content_cache_item, self).__init__(filename)

  def load(self, cached_filename):
    return file_util.read(cached_filename)
  
class file_cache(object):

  _log = logger('file_cache')
  
  _CACHE_DIR = path.join(path.expanduser('~'), '.bes', 'fs', 'cached_read')
  _CHECKSUMS_DIR_NAME = 'checksums'
  _FILES_DIR_NAME = 'files'
  _lock = Lock()

  @classmethod
  def cached_content(clazz, filename, cache_dir = None):
    'Return the cached content.'
    item = file_content_cache_item(filename)
    return clazz.cached_item(item, cache_dir)

  @classmethod
  def cached_filename(clazz, filename, cache_dir = None):
    'Return a temp file copy of filename.  It will delete when the process exits.'

    item = file_filename_cache_item(filename)
    clazz._log.log_d('file_cache:cached_filename: filename={} cache_dir={} item={}'.format(filename,
                                                                                           cache_dir,
                                                                                           item))
    result = clazz.cached_item(item, cache_dir = cache_dir)
    clazz._log.log_d('file_cache:cached_filename: result={}'.format(result))
    return result
  
  @classmethod
  def cached_item(clazz, item, cache_dir = None):
    cache_dir = cache_dir or clazz._CACHE_DIR
    clazz._log.log_d('file_cache:cached_item: item={} cache_dir={}'.format(item, cache_dir))
    try:
      clazz._lock.acquire()
      info = clazz._make_info(item, cache_dir)
      clazz._log.log_d('file_cache:cached_item: info={} cached_checksum={} checksum={}'.format(info,
                                                                                               info.cached_checksum,
                                                                                               item.checksum()))
      if info.cached_checksum != item.checksum():
        item.save(info)
      return item.load(info.cached_filename)
    finally:
      clazz._lock.release()

  @classmethod
  def _save(clazz, args, info, saver_func):
    try:
      saver_func(args, info)
    except IOError:
      # FIXME: write a unit test for this and figure out what the right exceptions to catch are
      file_util.remove([ info.cached_filename, info.checksum_filename ])

  @classmethod
  def _content_saver_func(clazz, args, info):
    filename = args[0]
    file_util.copy(filename, info.cached_filename)
    file_util.save(info.checksum_filename, info.checksum + line_break.DEFAULT_LINE_BREAK)

  @classmethod
  def _make_info(clazz, item, cache_dir):
    name = item.name()
    fragment_hash = str(hash(name) % ((sys.maxsize + 1) * 2))

    clazz._log.log_d('file_cache:_make_info: cache_dir={} _FILES_DIR_NAME={} _CHECKSUMS_DIR_NAME={} fragment_hash={}'.format(cache_dir,
                                                                                                                             clazz._FILES_DIR_NAME,
                                                                                                                             clazz._CHECKSUMS_DIR_NAME,
                                                                                                                             fragment_hash))
    cached_files_dir = path.join(cache_dir, clazz._FILES_DIR_NAME)
    cached_checksums_dir = path.join(cache_dir, clazz._CHECKSUMS_DIR_NAME)
    
    cached_filename = path.join(cached_files_dir, fragment_hash)
    checksum_filename = path.join(cached_checksums_dir, fragment_hash)
    clazz._log.log_d('file_cache:_make_info: cached_filename={} checksum_filename={}'.format(cached_filename,
                                                                                             checksum_filename))
    cached_checksum = clazz._cached_checksum(checksum_filename)
    return cache_info(cached_filename, checksum_filename, cached_checksum)

  @classmethod
  def _cached_checksum(clazz, checksum_filename):
    if path.exists(checksum_filename):
      return file_util.read(checksum_filename).strip()
    return None
