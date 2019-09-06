#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from abc import abstractmethod, ABCMeta
from bes.system.compat import with_metaclass
from bes.factory.singleton_class_registry import singleton_class_registry

from .vfs_registry import vfs_registry

class fs_register_meta(ABCMeta):
  
  def __new__(meta, name, bases, class_dict):
    clazz = ABCMeta.__new__(meta, name, bases, class_dict)
    if name != 'vfs_base':
      vfs_registry.register(clazz)
    return clazz

class vfs_base(with_metaclass(fs_register_meta, object)):
  'Abstract class to manipulate a filesystem.'

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
  def list_dir(self, remote_dir, recursive):
    'List entries in a directory.'
    pass

  @abstractmethod
  def has_file(self, remote_filename):
    'Return True if filename exists in the filesystem and is a FILE.'
    pass
  
  @abstractmethod
  def file_info(self, remote_filename):
    'Get info for a single file..'
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
  def download_file(self, remote_filename, local_filename):
    'Download filename to local_filename.'
    pass

  @abstractmethod
  def set_file_attributes(self, remote_filename, attributes):
    'Set file attirbutes.'
    pass
