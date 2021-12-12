#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os
import shutil
import subprocess

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
  def has_symlinks(self):
    'Return True if this system has support for symlinks.'
    return True

  @classmethod
  #@abstractmethod
  def remove_directory(self, d):
    'Recursively remove a directory.'
    shutil.rmtree(d)
