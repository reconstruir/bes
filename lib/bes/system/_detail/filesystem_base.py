#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from abc import abstractmethod, ABCMeta

class filesystem_base(object, metaclass = ABCMeta):
  'Abstract interface for dealing with system specific non portable filesystem stuff.'

  @classmethod
  @abstractmethod
  def free_disk_space(clazz, directory):
    'Return the free space for directory in bytes.'
    raise NotImplemented('free_disk_space')

  @classmethod
  @abstractmethod
  def sync(clazz):
    'Sync the filesystem.  Only works for both unix and windows in python3.  Otherwise only unix.'
    raise NotImplemented('sync')
  
  @classmethod
  @abstractmethod
  def has_symlinks(clazz):
    'Return True if this system has support for symlinks.'
    raise NotImplemented('has_symlinks')

  @classmethod
  @abstractmethod
  def remove_directory(clazz, d):
    'Recursively remove a directory.'
    raise NotImplemented('remove_directory')
  
  @classmethod
  @abstractmethod
  def max_filename_length(clazz):
    'Return the maximum allowed length for a filename.'
    raise NotImplemented('max_filename_length')

  @classmethod
  @abstractmethod
  def max_path_length(clazz):
    'Return the maximum allowed length for a path.'
    raise NotImplemented('max_path_length')

  @classmethod
  @abstractmethod
  def file_is_hidden(clazz, filename):
    'Return True if filename is a hidden file.'
    raise NotImplemented('file_is_hidden')
