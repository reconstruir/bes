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

class fs_git_repo(fs_base):
  'Masqurade a git repo as a filesystem.'

  log = logger('fs')
  
  def __init__(self, address, clone_manager_dir = None):
    check.check_string(address)
    check.check_string(clone_manager_dir, allow_none = True)
    self._address = address
    self._clone_manager_dir = clone_manager_dir or path.expanduser('~/.bes/git_clone_manager')

  def __str__(self):
    return 'fs_git_repo(address={})'.format(self._address)

  @classmethod
  #@abstractmethod
  def creation_fields(clazz):
    'Return a list of fields needed for create()'
    return [
      factory_field('address', False, check.is_string),
      factory_field('clone_manager_dir', True, check.is_string),
    ]
  
  @classmethod
  #@abstractmethod
  def create(clazz, **values):
    'Create an fs instance.'
    return fs_git_repo(values['local_root_dir'], cache_dir = values['cache_dir'])
    
  @classmethod
  #@abstractmethod
  def name(clazz):
    'The name if this fs.'
    return 'fs_git_repo'

  #@abstractmethod
  def list_dir(self, remote_dir, recursive):
    'List entries in a directory.'
    self.log.log_d('list_dir(remote_dir={}, recursive={}'.format(remote_dir, recursive))
    assert False
  
  #@abstractmethod
  def has_file(self, filename):
    'Return True if filename exists in the filesystem and is a FILE.'
    assert False
  
  #@abstractmethod
  def file_info(self, filename):
    'Get info for a single file..'
    assert False
  
  #@abstractmethod
  def remove_file(self, filename):
    'Remove filename.'
    assert False
  
  #@abstractmethod
  def upload_file(self, filename, local_filename):
    'Upload filename from local_filename.'
    assert False

  #@abstractmethod
  def download_file(self, filename, local_filename):
    'Download filename to local_filename.'
    assert False
    
  #@abstractmethod
  def set_file_attributes(self, filename, attributes):
    'Set file attirbutes.'
    assert False
