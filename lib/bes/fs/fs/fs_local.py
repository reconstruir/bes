#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from .fs_base import fs_base
from .fs_file_info import fs_file_info
from .fs_file_info_list import fs_file_info_list
from .fs_error import fs_error

from bes.fs.file_find import file_find
from bes.fs.file_util import file_util
from bes.fs.file_checksum import file_checksum
from bes.fs.file_attributes import file_attributes
from bes.system.log import logger

class fs_local(fs_base):

  log = logger('fs_local')
  
  def __init__(self, where):
    self._where = where
    file_util.mkdir(self._where)
  
  #@abstractmethod
  def list_dir(self, d, recursive):
    'List entries in a directory.'
    self.log.log_d('list_dir(d={}, recursive={}'.format(d, recursive))
    dir_path = self._make_dir_path(d)
    max_depth = None if recursive else 1
    self.log.log_d('list_dir: dir_path={}'.format(dir_path))
    files = file_find.find(dir_path, relative = True, max_depth = max_depth)
    result = fs_file_info_list()
    for filename in files:
      file_path = self._make_file_path(filename)
      entry = self._make_entry(filename, file_path)
      result.append(entry)
    return result

  #@abstractmethod
  def file_info(self, filename):
    'Get info for a single file..'
    p = self._make_file_path(filename)
    if not path.isfile(p):
      raise fs_error('file not found: {}'.format(filename))
    return self._make_entry(filename, p)
  
  #@abstractmethod
  def remove(self, filename):
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
  def upload(self, filename, local_filename):
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
  def set_attributes(self, filename, attributes):
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
  
  def _make_entry(self, filename, p):
    size = file_util.size(p)
    checksum = file_util.checksum('sha256', p)
    attributes = file_attributes.get_all(p)
    return fs_file_info(filename, size, checksum, attributes)
