#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from .detail.filesystem_base import filesystem_base
from .host import host

class filesystem(filesystem_base):

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
