#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from bes.common.check import check
from bes.common.node import node
from bes.fs.file_attributes import file_attributes
from bes.fs.file_checksum import file_checksum
from bes.fs.file_checksum_db import file_checksum_db
from bes.fs.file_find import file_find
from bes.fs.file_metadata import file_metadata
from bes.fs.file_util import file_util
from bes.system.log import logger
from bes.factory.factory_field import factory_field

from .fs_base import fs_base
from .fs_file_info import fs_file_info
from .fs_file_info_list import fs_file_info_list
from .fs_error import fs_error

class fs_local(fs_base):
  'Local filesystem'

  log = logger('fs')
  
  def __init__(self, local_root_dir, cache_dir = None):
    check.check_string(local_root_dir)
    check.check_string(cache_dir, allow_none = True)
    self._local_root_dir = local_root_dir
    self._cache_dir = cache_dir or path.expanduser('~/.bes/fs_local/cache')
    self._metadata_db_filename = path.join(self._cache_dir, 'metadata.db')
    self._checksum_db_filename = path.join(self._cache_dir, 'checksum.db')
    file_util.mkdir(self._local_root_dir)

  def __str__(self):
    return 'fs_local(local_root_dir={})'.format(self._local_root_dir)

  @classmethod
  #@abstractmethod
  def creation_fields(clazz):
    'Return a list of fields needed for create()'
    return [
      factory_field('local_root_dir', False, check.is_string),
      factory_field('cache_dir', True, check.is_string),
    ]
  
  @classmethod
  #@abstractmethod
  def create(clazz, **values):
    'Create an fs instance.'
    return fs_local(values['local_root_dir'], cache_dir = values['cache_dir'])
    
  @classmethod
  #@abstractmethod
  def name(clazz):
    'The name if this fs.'
    return 'fs_local'

  #@abstractmethod
  def list_dir(self, remote_dir, recursive):
    'List entries in a directory.'
    self.log.log_d('list_dir(remote_dir={}, recursive={}'.format(remote_dir, recursive))
    result = node('/')
    local_dir_path = self._make_local_dir_path(remote_dir)
    if not path.isdir(local_dir_path):
      raise fs_error('dir not found: {}'.format(remote_dir))
     
    max_depth = None if recursive else 1

    setattr(result, '_remote_filename', '/')
    setattr(result, '_local_filename', self._local_root_dir)
    setattr(result, '_is_file', False)
    
    for root, dirs, files in file_find.walk_with_depth(local_dir_path, max_depth = max_depth, follow_links = True):
      if root == local_dir_path:
        rel = '/'
      else:
        rel = file_util.ensure_lsep(file_util.remove_head(root, local_dir_path))
      files_set = set(files)
      for next_file_or_dir in sorted(files + dirs):
        remote_filename = path.join(rel, next_file_or_dir)
        assert remote_filename[0] == '/'
        remote_filename = remote_filename[1:]
        local_filename = path.join(root, next_file_or_dir)
        if self._should_include_file(local_filename):
          parts = remote_filename.split('/')
          new_node = result.ensure_path(parts)
          setattr(new_node, '_remote_filename', remote_filename)
          setattr(new_node, '_local_filename', local_filename)
          setattr(new_node, '_is_file', next_file_or_dir in files_set)

    fs_tree = self._convert_node_to_fs_tree(result, depth = 0)
    return fs_tree

  def _convert_node_to_fs_tree(self, n, depth = 0):
    indent = ' ' * depth
    is_file = getattr(n, '_is_file')
    remote_filename = getattr(n, '_remote_filename')
    local_filename = getattr(n, '_local_filename')
    if is_file:
      children = fs_file_info_list()
    else:
      children = fs_file_info_list([ self._convert_node_to_fs_tree(child, depth + 2) for child in n.children ])
    entry = self._make_entry(remote_filename, local_filename, children)
    return entry

  def _should_include_file(clazz, filename):
    return not file_util.is_hidden(filename)
  
  #@abstractmethod
  def has_file(self, filename):
    'Return True if filename exists in the filesystem and is a FILE.'
    p = self._make_local_file_path(filename)
    return path.isfile(p)
  
  #@abstractmethod
  def file_info(self, filename):
    'Get info for a single file..'
    p = self._make_local_file_path(filename)
    if not path.exists(p):
      raise fs_error('{}: not found: {}'.format(self, filename))
    local_filename = self._make_local_file_path(filename)
    return self._make_entry(filename, local_filename, fs_file_info_list())
  
  #@abstractmethod
  def remove_file(self, filename):
    'Remove filename.'
    p = self._make_local_file_path(filename)
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
    p = self._make_local_file_path(filename)
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
    p = self._make_local_file_path(filename)
    if not path.exists(p):
      raise fs_error('file not found: {}'.format(filename))
    if not path.isfile(p):
      raise fs_error('not a file: {}'.format(filename))
    file_util.copy(p, local_filename)
    
  #@abstractmethod
  def set_file_attributes(self, filename, attributes):
    'Set file attirbutes.'
    p = self._make_local_file_path(filename)
    if path.isdir(p):
      raise fs_error('filename exists and is a dir: {}'.format(filename))
    if path.exists(p) and not path.isfile(p):
      raise fs_error('filename exists and is not a file: {}'.format(filename))
    file_attributes.set_all(p, attributes)
  
  def _make_local_file_path(self, remote_filename):
    'Make a local path for remote_filename.'
    return path.join(self._local_root_dir, remote_filename)

  def _make_local_dir_path(self, remote_dir):
    'Make a local dir path.'
    if remote_dir == '/':
      return self._local_root_dir
    else:
      return path.join(self._local_root_dir, file_util.lstrip_sep(remote_dir))

  def _file_type(self, file_path):
    if path.isdir(file_path):
      return fs_file_info.DIR
    else:
      return fs_file_info.FILE
    
  def _make_entry(self, remote_filename, local_filename, children):
    ftype = self._file_type(local_filename)
    if ftype == fs_file_info.FILE:
      checksum = self._get_checksum(local_filename)
      attributes = file_attributes.get_all(local_filename)
      size = file_util.size(local_filename)
    else:
      checksum = None
      attributes = None
      size = None
    return fs_file_info(remote_filename, ftype, size, checksum, attributes, children)
    
  def _get_checksum(self, local_filename):
    db = file_checksum_db(self._metadata_db_filename)
    checksum = db.checksum('sha256', local_filename)
    return checksum

  def _get_attributes(self, local_filename):
    db = file_metadata(self._checksum_db_filename)
    return db.get_values(local_filename)

  def _files_filter(clazz, files):
    return [ f for f in files if not clazz._file_is_system_file(f) ]

  def _file_is_system_file(clazz, filename):
    b = path.basename(filename)
    return b.startswith('.bes')
