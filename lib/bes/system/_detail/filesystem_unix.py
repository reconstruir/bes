#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import errno
import os
import shutil
import subprocess

from ..compat import compat
from ..log import logger

from .filesystem_base import filesystem_base

class filesystem_unix(filesystem_base):

  _log = logger('filesystem')
  
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

    # Sometimes rmtree will raise an exception becasue
    # the "directory is not empty" which is bs.  It might
    # related to permissions in the underling files.
    #
    # Whenever that happens, we try again with ignore_errors = True
    # to workaround the issue.
    #
    # We *dont* always do this to not mask problems with other
    # none ENOTEMPTY codes
    try:
      shutil.rmtree(d)
      return
    except OSError as ex:
      if ex.errno != errno.ENOTEMPTY:
        clazz._log.log_exception(ex)
        raise
    try:
      shutil.rmtree(d, ignore_errors = True)
    except OSError as ex:
      clazz._log.log_exception(ex)
      raise

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
