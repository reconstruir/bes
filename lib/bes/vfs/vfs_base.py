#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from abc import abstractmethod, ABCMeta
from ..system.check import check
from bes.factory.singleton_class_registry import singleton_class_registry

from .vfs_registry import vfs_registry

class fs_register_meta(ABCMeta):
  
  def __new__(meta, name, bases, class_dict):
    clazz = ABCMeta.__new__(meta, name, bases, class_dict)
    if name != 'vfs_base':
      vfs_registry.register(clazz)
    return clazz

class vfs_base(object, metaclass = fs_register_meta):
  'Abstract class to manipulate a filesystem.'

  # vfs path separators are unix style for the same reason urls are
  SEP = '/'
  
  @classmethod
  @abstractmethod
  def creation_fields(clazz):
    'Return a list of fields needed for create()'
    pass
  
  @classmethod
  @abstractmethod
  def create(clazz, config_source, **values):
    'Create an fs instance.'
    pass
  
  @classmethod
  @abstractmethod
  def name(clazz):
    'The name of this fs.'
    pass

  @abstractmethod
  def list_dir(self, remote_dir, recursive, options):
    'Return a vfs_file_info_list() of entryes in a dir.'
    pass

  @abstractmethod
  def has_file(self, remote_filename):
    'Return True if filename exists in the filesystem and is a FILE.'
    pass
  
  @abstractmethod
  def file_info(self, remote_filename, options):
    'Get info for a single file or dir.'
    pass
  
  @abstractmethod
  def remove_file(self, remote_filename):
    'Remove filename.'
    pass
  
  @abstractmethod
  def upload_file(self, local_filename, remote_filename):
    'Upload local_filename to remote_filename.'
    pass

  @abstractmethod
  def download_to_file(self, remote_filename, local_filename):
    'Download filename to local_filename.'
    pass

  @abstractmethod
  def download_to_bytes(self, remote_filename):
    'Download filename to bytes.'
    pass

  @abstractmethod
  def set_file_attributes(self, remote_filename, attributes):
    'Set file attirbutes.'
    pass

  @abstractmethod
  def mkdir(self, remote_dir):
    'Create a remote dir.  Returns the fs specific directory id if appropiate or None'
    pass
  
check.register_class(vfs_base, name = 'vfs_fs')
