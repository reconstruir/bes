#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from abc import abstractmethod, ABCMeta
from bes.system.compat import with_metaclass
from bes.factory.singleton_class_registry import singleton_class_registry

from .fs_registry import fs_registry

class fs_register_meta(ABCMeta):
  
  def __new__(meta, name, bases, class_dict):
    clazz = ABCMeta.__new__(meta, name, bases, class_dict)
    if name != 'fs_base':
      fs_registry.register(clazz)
    return clazz

class fs_base(with_metaclass(fs_register_meta, object)):
  'Abstract class to manipulate a filesystem.'

  @classmethod
  @abstractmethod
  def create(clazz, config):
    'Create an fs instance.'
    pass
  
  @classmethod
  @abstractmethod
  def name(clazz):
    'The name if this fs.'
    pass

  @abstractmethod
  def list_dir(self, d, recursive):
    'List entries in a directory.'
    pass

  @abstractmethod
  def file_info(self, filename):
    'Get info for a single file..'
    pass
  
  @abstractmethod
  def remove_file(self, filename):
    'Remove filename.'
    pass
  
  @abstractmethod
  def upload_file(self, filename, local_filename):
    'Upload filename from local_filename.'
    pass

  @abstractmethod
  def download_file(self, filename, local_filename):
    'Download filename to local_filename.'
    pass

  @abstractmethod
  def set_file_attributes(self, filename, attributes):
    'Set file attirbutes.'
    pass
