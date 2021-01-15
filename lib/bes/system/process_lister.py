#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import platform

from .detail.process_lister_base import process_lister_base

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
    system = platform.system()
    if system == 'Linux':
      from .detail.process_lister_linux import process_lister_linux
      return process_lister_linux
    elif system == 'Darwin':
      from .detail.process_lister_macos import process_lister_macos
      return process_lister_macos
    elif system == 'Windows':
      from .detail.process_lister_windows import process_lister_windows
      return process_lister_windows
    else:
      return None
