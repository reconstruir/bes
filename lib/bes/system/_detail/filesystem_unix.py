#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os
import shutil
import subprocess
import os.path as path

from bes.system.compat import compat

from .filesystem_base import filesystem_base

class filesystem_unix(filesystem_base):

  @classmethod
  #@abstractmethod
  def free_disk_space(clazz, directory):
    'Return the free space for directory in bytes.'
    stat = os.statvfs(directory)
    bytes_free = stat.f_frsize * stat.f_bavail
    return bytes_free

  @classmethod
  #@abstractmethod
  def sync(clazz):
    'Sync the filesystem.'
    if compat.IS_PYTHON3:
      os.sync()
    else:
      subprocess.call([ 'sync' ])

  @classmethod
  #@abstractmethod
  def has_symlinks(clazz):
    'Return True if this system has support for symlinks.'
    return True

  @classmethod
  #@abstractmethod
  def remove_directory(clazz, d):
    'Recursively remove a directory.'
    shutil.rmtree(d)

  @classmethod
  #@abstractmethod
  def max_filename_length(clazz):
    'Return the maximum allowed length for a filename.'
    return os.pathconf('/', 'PC_NAME_MAX')

  @classmethod
  #@abstractmethod
  def max_path_length(clazz):
    'Return the maximum allowed length for a path.'
    return os.pathconf('/', 'PC_PATH_MAX')

  @classmethod
  #@abstractmethod
  def file_is_hidden(clazz, filename):
    'Return True if filename is a hidden file.'
    normalized_filename = path.normpath(path.abspath(filename))
    basename = path.basename(normalized_filename)
    return basename.startswith('.')

  @classmethod
  #@abstractmethod
  def filesystem_id(clazz, filename):
    'Return the id for the filesystem filename is found in.'
    statvfs = os.statvfs(filename)
    return statvfs.f_fsid
