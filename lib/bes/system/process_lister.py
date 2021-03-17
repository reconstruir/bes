#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from .detail.process_lister_base import process_lister_base
from .host import host

class process_lister(process_lister_base):

  def _find_impl_class():
    if host.is_linux():
      from .detail.process_lister_linux import process_lister_linux
      return process_lister_linux
    elif host.is_macos():
      from .detail.process_lister_macos import process_lister_macos
      return process_lister_macos
    elif host.is_windows():
      from .detail.process_lister_windows import process_lister_windows
      return process_lister_windows
    else:
      host.raise_unsupported_system()
  
  _impl_class = _find_impl_class()

  @classmethod
  #@abstractmethod
  def list_processes(clazz):
    'List all processes.'
    return clazz._impl_class.list_processes()

  @classmethod
  #@abstractmethod
  def open_files(clazz, pid):
    'Return a list of open files for pid or None if pid not found.'
    return clazz._impl_class.open_files(pid)
  
  @classmethod
  def _find_impl_class(clazz):
    if host.is_linux():
      from .detail.process_lister_linux import process_lister_linux
      return process_lister_linux
    elif host.is_macos():
      from .detail.process_lister_macos import process_lister_macos
      return process_lister_macos
    elif host.is_windows():
      from .detail.process_lister_windows import process_lister_windows
      return process_lister_windows
    else:
      host.raise_unsupported_system()
