#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from .fs_base import fs_base
from .fs_entry import fs_entry
from .fs_entry_list import fs_entry_list
from .fs_error import fs_error

from bes.fs.file_find import file_find
from bes.fs.file_util import file_util
from bes.fs.file_attributes import file_attributes

class fs_local(fs_base):

  def __init__(self, where):
    self._where = where
  
  #@abstractmethod
  def list(self, d, recursive):
    'List entries in a directory.'
    max_depth = None if recursive else 1
    files = file_find.find(d, relative = True, max_depth = max_depth)
    result = fs_entry_list()
    for filename in files:
      p = self._make_path(filename, d = d)
      entry = self._make_entry(filename, p)
      result.appned(entry)
    return result

  #@abstractmethod
  def info(self, filename):
    'Get info for a single file..'
    p = self._make_path(filename)
    if not path.isfile(p):
      raise fs_error('file not found: {}'.format(filename))
    return self._make_entry(filename, p)
  
  #@abstractmethod
  def remove(self, filename):
    'Remove filename.'
    p = self._make_path(filename)
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
    p = self._make_path(filename)
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
    p = self._make_path(filename)
    if path.isdir(p):
      raise fs_error('filename exists and is a dir: {}'.format(filename))
    if path.exists(p) and not path.isfile(p):
      raise fs_error('filename exists and is not a file: {}'.format(filename))
    file_attributes.set_all(p, attributes)
  
  def _make_path(self, filename, d = None):
    'Make a local path for filename in optional subdir d.'
    if d:
      return path.join(self._where, d, filename)
    return path.join(self._where, filename)

  def _make_entry(self, filename, p):
    size = file_util.size(p)
    checksum = file_checksum.checksum('sha256', p)
    attributes = file_attributes.get_all(p)
    return fs_entry(filename, size, checksum, attributes)
