#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from abc import abstractmethod, ABCMeta

class filesystem_base(object, metaclass = ABCMeta):
  'Abstract interface for dealing with system specific non portable filesystem stuff.'

  @classmethod
  @abstractmethod
  def free_disk_space(clazz, directory):
    'Return the free space for directory in bytes.'
    raise NotImplementedError('free_disk_space')

  @classmethod
  @abstractmethod
  def sync(clazz):
    'Sync the filesystem.  Only works for both unix and windows in python3.  Otherwise only unix.'
    raise NotImplementedError('sync')
  
  @classmethod
  @abstractmethod
  def has_symlinks(clazz):
    'Return True if this system has support for symlinks.'
    raise NotImplementedError('has_symlinks')

  @classmethod
  @abstractmethod
  def remove_directory(clazz, d):
    'Recursively remove a directory.'
    raise NotImplementedError('remove_directory')
  
  @classmethod
  @abstractmethod
  def max_filename_length(clazz):
    'Return the maximum allowed length for a filename.'
    raise NotImplementedError('max_filename_length')

  @classmethod
  @abstractmethod
  def max_path_length(clazz):
    'Return the maximum allowed length for a path.'
    raise NotImplementedError('max_path_length')

  @classmethod
  @abstractmethod
  def file_is_hidden(clazz, filename):
    'Return True if filename is a hidden file.'
    raise NotImplementedError('file_is_hidden')

  @classmethod
  @abstractmethod
  def filesystem_id(clazz, filename):
    'Return the id for the filesystem filename is found in.'
    raise NotImplementedError('filesystem_id')

  @classmethod
  @abstractmethod
  def hard_link_count(clazz, filename):
    'Return the number of hard links for a file.'
    raise NotImplementedError('hard_link_count')
  
