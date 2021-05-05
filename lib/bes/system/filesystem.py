#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import atexit
import errno
import os
import os.path as path

from .compat import compat
from .host import host
from .log import logger

from .detail.filesystem_base import filesystem_base

class filesystem(filesystem_base):

  _log = logger('filesystem')
  
  def _find_impl_class():
    result = None
    if host.is_unix():
      from .detail.filesystem_unix import filesystem_unix
      result = filesystem_unix
    elif host.is_windows():
      from .detail.filesystem_windows import filesystem_windows
      result = filesystem_windows
    return result
  
  _impl_class = _find_impl_class()
  if not _impl_class:
    host.raise_unsupported_system()
  
  def __init__(self):
    pass
    
  @classmethod
  #@abstractmethod
  def free_disk_space(clazz, directory):
    'Return the free space for directory in bytes.'
    return clazz._impl_class.free_disk_space(directory)

  @classmethod
  #@abstractmethod
  def sync(clazz):
    'Sync the filesystem.'
    return clazz._impl_class.sync()

  @classmethod
  #@abstractmethod
  def has_symlinks(clazz):
    'Return True if this system has support for symlinks.'
    return clazz._impl_class.has_symlinks()

  @classmethod
  #@abstractmethod
  def remove_directory(clazz, d):
    'Recursively remove a directory.'
    return clazz._impl_class.remove_directory(d)
  
  @classmethod
  def remove(clazz, files, raise_not_found_error = False):
    '''
    Remove a mixutre of files, directories or a list of files and directories.
    Errors are propagated unless its file not found in which case it is
    only propagated if raise_not_found_error is True.
    '''
    if isinstance(files, compat.STRING_TYPES):
      files = [ files ]
    for f in files:
      try:
        if path.isdir(f):
          clazz.remove_directory(f)
        else:
          os.remove(f)
      except OSError as ex:
        if ex.errno != errno.ENOENT:
          raise
        if raise_not_found_error:
          raise
      except Exception as ex:
        clazz._log.log_e('file_util.remove: Caught exception {}:{} removing "{}"'.format(str(ex), type(ex), f))
  
  @classmethod
  def atexit_remove(clazz, f):
    'Remove a file or directory at exit time'
    def _do_remove(*args, **kargs):
      _arg_f = args[0]
      filesystem.remove(_arg_f)
    atexit.register(_do_remove, f)
