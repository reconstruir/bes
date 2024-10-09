#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os, subprocess
from os import path

from ..system.check import check
from bes.common.node import node
from bes.factory.factory_field import factory_field
from bes.fs.checksum import checksum
from bes.fs.checksum_set import checksum_set
from bes.fs.file_attributes import file_attributes
from bes.fs.file_checksum_db import file_checksum_db
from bes.fs.file_metadata import file_metadata
from bes.fs.file_util import file_util
from bes.key_value.key_value_list import key_value_list
from bes.system.log import logger

from ..files.find.bf_file_finder import bf_file_finder

from .vfs_base import vfs_base
from .vfs_error import vfs_error
from .vfs_file_info import vfs_file_info
from .vfs_file_info import vfs_file_info_list
from .vfs_file_info_options import vfs_file_info_options
from .vfs_path_util import vfs_path_util
from .vfs_file_find import vfs_file_find

class vfs_local(vfs_base):
  'Local filesystem'

  log = logger('vfs_local')
  
  def __init__(self, config_source, local_root_dir):
    check.check_string(config_source)
    check.check_string(local_root_dir)

    self._config_source = config_source
    self._local_root_dir = local_root_dir
    self._db_dir = path.join(self._local_root_dir, '.bes_vfs')
    self._metadata_db_filename = path.join(self._db_dir, 'metadata.db')
    self._checksum_db_filename = path.join(self._db_dir, 'checksum.db')

  def __str__(self):
    return 'vfs_local(local_root_dir={})'.format(self._local_root_dir)

  @classmethod
  #@abstractmethod
  def creation_fields(clazz):
    'Return a list of fields needed for create()'
    return [
      factory_field('local_root_dir', False, check.is_string),
    ]
  
  @classmethod
  #@abstractmethod
  def create(clazz, config_source, **values):
    'Create an fs instance.'
    return vfs_local(config_source, values['local_root_dir'])
    
  @classmethod
  #@abstractmethod
  def name(clazz):
    'The name if this fs.'
    return 'vfs_local'

  #@abstractmethod
  def list_dir(self, remote_dir, recursive, options):
    'List entries in a directory.'
    check.check_string(remote_dir)
    check.check_bool(recursive)
    check.check_vfs_file_info_options(options, allow_none = True)

    remote_dir = vfs_path_util.normalize(remote_dir)
    options = options or vfs_file_info_options()
    
    result = node(self.SEP)
    local_dir_path = self._make_local_dir_path(remote_dir)
    self.log.log_d('list_dir: remote_dir={} recursive={} local_dir_path={}'.format(remote_dir, recursive, local_dir_path))
    if not path.exists(local_dir_path):
      raise vfs_error('dir does not exist: {}'.format(remote_dir))

    if not path.isdir(local_dir_path):
      raise vfs_error('not a dir: {}'.format(remote_dir))
    
    max_depth = None if recursive else 1
    setattr(result, '_remote_filename', self.SEP)
    setattr(result, '_local_filename', self._local_root_dir)
    setattr(result, '_is_file', False)

    num_added = 0
    for root, dirs, files in vfs_file_find.walk_with_depth(local_dir_path, max_depth = max_depth, follow_links = True):
      if root == local_dir_path:
        rel = os.sep
      else:
        rel = file_util.ensure_lsep(file_util.remove_head(root, local_dir_path))
      self.log.log_d('list_dir: next: root={} dirs={} files={} rel={}'.format(root, dirs, files, rel))
      files_set = set(files)
      if not self._should_include_file(rel):
        self.log.log_d('list_dir: skipping {}'.format(rel))
        continue
      for next_file_or_dir in sorted(files + dirs):
        if self._should_include_file(next_file_or_dir):
          self.log.log_d('list_dir: rel={} next_file_or_dir={}'.format(rel, next_file_or_dir))
          local_filename_rel = path.join(rel, next_file_or_dir)
          remote_filename = local_filename_rel.replace(os.sep, self.SEP)
          self.log.log_d('list_dir: local_filename_rel={} remote_filename={}'.format(local_filename_rel,
                                                                                     remote_filename))
          assert local_filename_rel[0] == os.sep
          assert remote_filename[0] == self.SEP
          remote_filename = remote_filename[1:]
          local_filename = path.join(root, next_file_or_dir)
          parts = remote_filename.split('/')
          new_node = result.ensure_path(parts)
          setattr(new_node, '_remote_filename', remote_filename)
          setattr(new_node, '_local_filename', local_filename)
          setattr(new_node, '_is_file', next_file_or_dir in files_set)
          num_added += 1
        else:
          self.log.log_d('list_dir: skipping {}'.format(next_file_or_dir))
    if num_added == 0:
      return vfs_file_info_list()
    fs_tree = self._convert_node_to_fs_tree(result, 0, options)
    return fs_tree.children

  def _convert_node_to_fs_tree(self, n, depth, options):
    if not hasattr(n, '_is_file'):
      msg = 'node missing attributes:\n----------------------\n{}\n----------------------\n'.format(n)
      raise RuntimeError(msg)
    indent = ' ' * depth
    is_file = getattr(n, '_is_file')
    remote_filename = getattr(n, '_remote_filename')
    local_filename = getattr(n, '_local_filename')
    if is_file:
      children = vfs_file_info_list()
    else:
      children = vfs_file_info_list([ self._convert_node_to_fs_tree(child, depth + 2, options) for child in n.children ])
    entry = self._make_entry(remote_filename, local_filename, children, options)
    return entry

  def _should_include_file(clazz, filename):
    return not file_util.is_hidden(filename)
  
  #@abstractmethod
  def has_file(self, remote_filename):
    'Return True if filename exists in the filesystem and is a FILE.'
    remote_filename = vfs_path_util.normalize(remote_filename)
    p = self._make_local_file_path(remote_filename)
    return path.isfile(p)
  
  #@abstractmethod
  def file_info(self, remote_filename, options):
    'Get info for a single file.'
    check.check_string(remote_filename)
    check.check_vfs_file_info_options(options, allow_none = True)

    remote_filename = vfs_path_util.normalize(remote_filename)
    options = options or vfs_file_info_options()

    p = self._make_local_file_path(remote_filename)
    if not path.exists(p):
      raise vfs_error('{}: not found: {}'.format(self, remote_filename))
    local_filename = self._make_local_file_path(remote_filename)
    return self._make_entry(remote_filename, local_filename, vfs_file_info_list(), options)
  
  #@abstractmethod
  def remove_file(self, remote_filename):
    'Remove filename.'
    remote_filename = vfs_path_util.normalize(remote_filename)
    p = self._make_local_file_path(remote_filename)
    if not path.exists(p):
      raise vfs_error('file not found: {}'.format(remote_filename))
    if path.isdir(p):
      raise vfs_error('should be file instead of dir: {}'.format(remote_filename))
    if not path.isfile(p):
      raise vfs_error('not a file: {}'.format(remote_filename))
    file_util.remove(p)
  
  #@abstractmethod
  def upload_file(self, local_filename, remote_filename):
    'Upload local_filename to remote_filename.'
    remote_filename = vfs_path_util.normalize(remote_filename)
    p = self._make_local_file_path(remote_filename)
    if path.isdir(p):
      raise vfs_error('filename exists and is a dir: {}'.format(remote_filename))
    if path.exists(p) and not path.isfile(p):
      raise vfs_error('filename exists and is not a file: {}'.format(remote_filename))
    if not path.exists(local_filename):
      raise vfs_error('local_filename not found: {}'.format(local_filename))
    file_util.copy(local_filename, p)
    file_util.sync()

  #@abstractmethod
  def download_to_file(self, remote_filename, local_filename):
    'Download filename to local_filename.'
    remote_filename = vfs_path_util.normalize(remote_filename)
    p = self._make_local_file_path(remote_filename)
    if not path.exists(p):
      raise vfs_error('file not found: {}'.format(remote_filename))
    if not path.isfile(p):
      raise vfs_error('not a file: {}'.format(remote_filename))
    file_util.copy(p, local_filename)
    
  #@abstractmethod
  def download_to_bytes(self, remote_filename):
    'Download filename to local_filename.'
    remote_filename = vfs_path_util.normalize(remote_filename)
    p = self._make_local_file_path(remote_filename)
    if not path.exists(p):
      raise vfs_error('file not found: {}'.format(remote_filename))
    if not path.isfile(p):
      raise vfs_error('not a file: {}'.format(remote_filename))
    return file_util.read(p)
    
  #@abstractmethod
  def set_file_attributes(self, remote_filename, attributes):
    'Set file attirbutes.'
    remote_filename = vfs_path_util.normalize(remote_filename)
    local_filename = self._make_local_file_path(remote_filename)
    if path.isdir(local_filename):
      raise vfs_error('filename exists and is a dir: {}'.format(remote_filename))
    if path.exists(local_filename) and not path.isfile(local_filename):
      raise vfs_error('filename exists and is not a file: {}'.format(remote_filename))
    db = file_metadata(self._metadata_db_filename)    
    db.replace_values('attributes', local_filename, key_value_list.from_dict(attributes))
  
  def _make_local_file_path(self, remote_filename):
    'Make a local path for remote_filename.'
    return path.join(self._local_root_dir, file_util.lstrip_sep(remote_filename))

  def _make_local_dir_path(self, remote_dir):
    'Make a local dir path.'
    if remote_dir == self.SEP:
      return self._local_root_dir
    else:
      return file_util.rstrip_sep(path.join(self._local_root_dir, file_util.lstrip_sep(remote_dir)))

  def _file_type(self, file_path):
    if path.isdir(file_path):
      return vfs_file_info.DIR
    else:
      return vfs_file_info.FILE

  def _make_entry(self, remote_filename, local_filename, children, options):
    ftype = self._file_type(local_filename)
    if ftype == vfs_file_info.FILE:
      chk = checksum_set(checksum(checksum.SHA256, self._get_checksum(local_filename)))
      db = file_metadata(self._metadata_db_filename)    
      attributes = db.get_values('attributes', local_filename).to_dict()
      size = file_util.size(local_filename)
    else:
      chk = None
      attributes = None
      size = None
    if options.hardcode_modification_date:
      modification_date = options.hardcode_modification_date
    else:
      modification_date = file_util.get_modification_date(local_filename)
    return vfs_file_info(remote_filename,
                         ftype,
                         modification_date,
                         size,
                         chk,
                         attributes,
                         children)
    
  def _get_checksum(self, local_filename):
    db = file_checksum_db(self._checksum_db_filename)
    checksum = db.checksum('sha256', local_filename)
    return checksum

  #@abstractmethod
  def mkdir(self, remote_dir):
    'Create a remote dir.  Returns the fs specific directory id if appropiate or None'
    remote_dir = vfs_path_util.normalize(remote_dir)
    p = self._make_local_file_path(remote_dir)
    if path.exists(p):
      if not path.isdir(p):
        raise vfs_error('already a file: {}'.format(remote_dir))
      return None
    file_util.mkdir(p)
