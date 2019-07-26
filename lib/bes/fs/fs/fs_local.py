#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from bes.common.check import check
from bes.fs.file_attributes import file_attributes
from bes.fs.file_checksum import file_checksum
from bes.fs.file_checksum_db import file_checksum_db
from bes.fs.file_find import file_find
from bes.fs.file_metadata import file_metadata
from bes.fs.file_util import file_util
from bes.system.log import logger

from .fs_base import fs_base
from .fs_file_info import fs_file_info
from .fs_file_info_list import fs_file_info_list
from .fs_error import fs_error

class fs_local(fs_base):
  'Local filesystem'

  log = logger('fs_local')
  
  def __init__(self, where, cache_dir = None):
    check.check_string(where)
    check.check_string(cache_dir, allow_none = True)
    self._where = where
    self._cache_dir = cache_dir or path.expanduser('~/.bes/fs_local/cache')
    self._metadata_db_filename = path.join(self._cache_dir, 'metadata.db')
    self._checksum_db_filename = path.join(self._cache_dir, 'checksum.db')
    file_util.mkdir(self._where)

  def __str__(self):
    return 'fs_local(where={}, cache_dir={})'.format(self._where, self._cache_dir)
    
  @classmethod
  #@abstractmethod
  def create(clazz, config):
    'Create an fs instance.'
    check.check_fs_config(config)
    assert config.fs_type == clazz.name()
    where = config.values.get('where', None)
    if where is None:
      raise fs_error('Need "where" to create an fs_local')
    cache_dir = config.values.get('cache_dir', None)
    return fs_local(where, cache_dir = cache_dir)
    
  @classmethod
  #@abstractmethod
  def name(clazz):
    'The name if this fs.'
    return 'fs_local'
    
  #@abstractmethod
  def list_dir(self, d, recursive):
    'List entries in a directory.'
    self.log.log_d('list_dir(d={}, recursive={}'.format(d, recursive))
    dir_path = self._make_dir_path(d)
    max_depth = None if recursive else 1
    self.log.log_d('list_dir: dir_path={}'.format(dir_path))
    files = file_find.find(dir_path, relative = True, max_depth = max_depth,
                           file_type = file_find.FILE|file_find.LINK|file_find.DIR)
    files = self._files_filter(files)
    result = fs_file_info_list()
    for filename in files:
      file_path = self._make_file_path(filename)
      entry = self._make_entry(filename, file_path)
      result.append(entry)
    return result

  #@abstractmethod
  def has_file(self, filename):
    'Return True if filename exists in the filesystem and is a FILE.'
    p = self._make_file_path(filename)
    return path.isfile(p)
  
  #@abstractmethod
  def file_info(self, filename):
    'Get info for a single file..'
    p = self._make_file_path(filename)
    if not path.isfile(p):
      raise fs_error('file not found: {}'.format(filename))
    return self._make_entry(filename, p)
  
  #@abstractmethod
  def remove_file(self, filename):
    'Remove filename.'
    p = self._make_file_path(filename)
    if not path.exists(p):
      raise fs_error('file not found: {}'.format(filename))
    if path.isdir(p):
      raise fs_error('should be file instead of dir: {}'.format(filename))
    if not path.isfile(p):
      raise fs_error('not a file: {}'.format(filename))
    file_util.remove(p)
  
  #@abstractmethod
  def upload_file(self, filename, local_filename):
    'Upload filename from local_filename.'
    p = self._make_file_path(filename)
    if path.isdir(p):
      raise fs_error('filename exists and is a dir: {}'.format(filename))
    if path.exists(p) and not path.isfile(p):
      raise fs_error('filename exists and is not a file: {}'.format(filename))
    if not path.exists(local_filename):
      raise fs_error('local_filename not found: {}'.format(local_filename))
    file_util.copy(local_filename, p)

  #@abstractmethod
  def download_file(self, filename, local_filename):
    'Download filename to local_filename.'
    p = self._make_file_path(filename)
    if not path.exists(p):
      raise fs_error('file not found: {}'.format(filename))
    if not path.isfile(p):
      raise fs_error('not a file: {}'.format(filename))
    file_util.copy(p, local_filename)
    
  #@abstractmethod
  def set_file_attributes(self, filename, attributes):
    'Set file attirbutes.'
    p = self._make_file_path(filename)
    if path.isdir(p):
      raise fs_error('filename exists and is a dir: {}'.format(filename))
    if path.exists(p) and not path.isfile(p):
      raise fs_error('filename exists and is not a file: {}'.format(filename))
    file_attributes.set_all(p, attributes)
  
  def _make_file_path(self, filename, d = None):
    'Make a local path for filename in optional subdir d.'
    if d:
      return path.join(self._where, d, filename)
    return path.join(self._where, filename)

  def _make_dir_path(self, d):
    'Make a local dir path.'
    if d == '/':
      return self._where
    else:
      return path.join(self._where, file_util.lstrip_sep(d))

  def _file_type(self, file_path):
    if path.isdir(file_path):
      return fs_file_info.DIR
    else:
      return fs_file_info.FILE
    
  def _make_entry(self, filename, file_path):
    ftype = self._file_type(file_path)
    if ftype == fs_file_info.FILE:
      checksum = self._get_checksum(file_path)
      attributes = file_attributes.get_all(file_path)
      size = file_util.size(file_path)
    else:
      checksum = None
      attributes = None
      size = None
    return fs_file_info(filename, ftype, size, checksum, attributes)
    
  def _get_checksum(self, file_path):
    db = file_checksum_db(self._metadata_db_filename)
    checksum = db.checksum('sha256', file_path)
    return checksum

  def _get_attributes(self, file_path):
    db = file_metadata(self._checksum_db_filename)
    return db.get_values()

  def _files_filter(clazz, files):
    return [ f for f in files if not clazz._file_is_system_file(f) ]

  def _file_is_system_file(clazz, filename):
    b = path.basename(filename)
    return b.startswith('.bes')
