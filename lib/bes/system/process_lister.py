#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from .detail.process_lister_base import process_lister_base
from .host import host

class process_lister(process_lister_base):

  def __init__(self):
    impl_class = self._find_impl_class()
    if not impl_class:
      raise RuntimeError('Unknown system: {}'.format(system))
    self._impl = impl_class()
    
  #@abstractmethod
  def list_processes(self):
    'List all processes.'
    return self._impl.list_processes()

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
