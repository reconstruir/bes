#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from abc import abstractmethod, ABCMeta
from bes.system.compat import with_metaclass

class filesystem_base(with_metaclass(ABCMeta, object)):
  'Abstract interface for dealing with system specific non portable filesystem stuff.'

  @classmethod
  @abstractmethod
  def free_disk_space(self, directory):
    'Return the free space for directory in bytes.'
    raise NotImplemented('free_disk_space')

  @classmethod
  @abstractmethod
  def sync(self):
    'Sync the filesystem.  Only works for both unix and windows in python3.  Otherwise only unix.'
    raise NotImplemented('sync')
  
  @classmethod
  @abstractmethod
  def has_symlinks(self):
    'Return True if this system has support for symlinks.'
    raise NotImplemented('has_symlinks')

  @classmethod
  @abstractmethod
  def remove_directory(self, d):
    'Recursively remove a directory.'
    raise NotImplemented('remove_directory')
  
  @classmethod
  @abstractmethod
  def max_filename_length(self):
    'Return the maximum allowed length for a filename.'
    raise NotImplemented('max_filename_length')

  @classmethod
  @abstractmethod
  def max_path_length(self):
    'Return the maximum allowed length for a path.'
    raise NotImplemented('max_path_length')
