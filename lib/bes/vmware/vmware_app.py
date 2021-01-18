#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import platform

from .vmware_app_base import vmware_app_base

class vmware_app(vmware_app_base):

  def __init__(self):
    impl_class = self._find_impl_class()
    if not impl_class:
      raise RuntimeError('Unknown system: {}'.format(system))
    self._impl = impl_class()
    
  #@abstractmethod
  def is_installed(self):
    'Return True if vmware is installed.'
    return self._impl.is_installed()

  #@abstractmethod
  def is_running(self):
    'Return True if vmware is running.'
    return self._impl.is_running()

  #@abstractmethod
  def ensure_running(self):
    'Ensure vmware is running.'
    self._impl.ensure_running()

  @classmethod
  def _find_impl_class(clazz):
    system = platform.system()
    if system == 'Linux':
      from .vmware_app_linux import vmware_app_linux
      return vmware_app_linux
    elif system == 'Darwin':
      from .vmware_app_macos import vmware_app_macos
      return vmware_app_macos
    elif system == 'Windows':
      from .vmware_app_windows import vmware_app_windows
      return vmware_app_windows
    else:
      return None
