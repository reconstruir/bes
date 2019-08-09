#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path
from collections import namedtuple

from bes.common.check import check
from bes.common.node import node
from bes.fs.file_attributes import file_attributes
from bes.fs.file_checksum import file_checksum
from bes.fs.file_checksum_db import file_checksum_db
from bes.fs.file_find import file_find
from bes.fs.file_metadata import file_metadata
from bes.fs.file_util import file_util
from bes.fs.file_mime import file_mime
from bes.system.log import logger
from bes.factory.factory_field import factory_field
from bes.git.git_clone_manager import git_clone_manager

from .fs_base import fs_base
from .fs_file_info import fs_file_info
from .fs_file_info_list import fs_file_info_list
from .fs_error import fs_error
from .fs_local import fs_local

class fs_git_repo(fs_base):
  'Masquerade a git repo as a filesystem.  All operations are committed automatically.'

  log = logger('fs')
  
  def __init__(self, address, config_dir, use_lfs):
    check.check_string(address)
    check.check_string(config_dir)
    self._address = address
    self._config_dir = config_dir
    self._use_lfs = use_lfs
    clone_manager_dir = path.join(self._config_dir, 'clone')
    self._clone_manager = git_clone_manager(clone_manager_dir)

  def __str__(self):
    return 'fs_git_repo(address={})'.format(self._address)

  @classmethod
  #@abstractmethod
  def creation_fields(clazz):
    'Return a list of fields needed for create()'
    return [
      factory_field('address', False, check.is_string),
      factory_field('config_dir', False, check.is_string),
      factory_field('use_lfs', False, factory_field.is_bool),
    ]
  
  @classmethod
  #@abstractmethod
  def create(clazz, **values):
    'Create an fs instance.'
    return fs_git_repo(values['address'], values['config_dir'], values['use_lfs'])
    
  @classmethod
  #@abstractmethod
  def name(clazz):
    'The name of this fs.'
    return 'fs_git_repo'

  #@abstractmethod
  def list_dir(self, remote_dir, recursive):
    'List entries in a directory.'
    self.log.log_d('list_dir(remote_dir={}, recursive={}'.format(remote_dir, recursive))
    proxy = self._make_proxy()
    return proxy.fs.list_dir(remote_dir, recursive)
  
  #@abstractmethod
  def has_file(self, remote_filename):
    'Return True if filename exists in the filesystem and is a FILE.'
    proxy = self._make_proxy()
    return proxy.fs.has_file(remote_filename)
  
  #@abstractmethod
  def file_info(self, remote_filename):
    'Get info for a single file..'
    proxy = self._make_proxy()
    return proxy.fs.file_info(remote_filename)
  
  #@abstractmethod
  def remove_file(self, filename):
    'Remove filename.'
    proxy = self._make_proxy()
    proxy.repo.remove(filename)
    comment = 'remove {}'.format(filename)
    proxy.repo.commit(comment, filename)
    proxy.repo.push()
  
  #@abstractmethod
  def upload_file(self, local_filename, remote_filename):
    'Upload local_filename to remote_filename.'
    proxy = self._make_proxy()
    proxy.fs.upload_file(local_filename, remote_filename)
    proxy.repo.add(remote_filename)
    if self._use_lfs:
      if not file_mime.content_is_text(local_filename):
        pattern = '*.{}'.format(file_util.extension(remote_filename))
        proxy.repo.lfs_track(remote_filename)
    comment = 'add {}'.format(remote_filename)
    proxy.repo.commit(comment, remote_filename)
    st = proxy.repo.status('.')
    print('status: {}'.format(st))
    proxy.repo.push()

  #@abstractmethod
  def download_file(self, remote_filename, local_filename):
    'Download filename to local_filename.'
    proxy = self._make_proxy()
    return proxy.fs.download_file(remote_filename, local_filename)
    
  #@abstractmethod
  def set_file_attributes(self, remote_filename, attributes):
    'Set file attirbutes.'
    proxy = self._make_proxy()
    proxy.fs.set_file_attributes(remote_filename, attributes)

  class _proxy(namedtuple('_proxy', 'repo, fs')):

    def __new__(clazz, repo, fs):
      return clazz.__bases__[0].__new__(clazz, repo, fs)
    
  def _make_proxy(self):
    repo = self._clone_manager.update(self._address)
    fs = fs_local(repo.root)
    return self._proxy(repo, fs)
    
