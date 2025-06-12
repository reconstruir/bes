#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from .bat_vmware_app_base import bat_vmware_app_base

def _find_impl_class():
  from bes.system.host import host
  if host.is_linux():
    from .bat_vmware_app_linux import bat_vmware_app_linux
    return bat_vmware_app_linux
  elif host.is_macos():
    from .bat_vmware_app_macos import bat_vmware_app_macos
    return bat_vmware_app_macos
  elif host.is_windows():
    from .bat_vmware_app_windows import bat_vmware_app_windows
    return bat_vmware_app_windows
  else:
    host.raise_unsupported_system()

class bat_vmware_app(bat_vmware_app_base):

  _impl = _find_impl_class()

  @classmethod
  #@abstractmethod
  def install_path(clazz):
    'The full path to where vmware is installed.'
    return clazz._impl.install_path()
  
  @classmethod
  #@abstractmethod
  def is_installed(clazz):
    'Return True if vmware is installed.'
    return clazz._impl.is_installed()

  @classmethod
  #@abstractmethod
  def is_running(clazz):
    'Return True if vmware is running.'
    return clazz._impl.is_running()

  @classmethod
  #@abstractmethod
  def ensure_running(clazz):
    'Ensure vmware is running.'
    clazz._impl.ensure_running()

  @classmethod
  #@abstractmethod
  def ensure_stopped(clazz):
    'Ensure vmware is stopped.'
    clazz._impl.ensure_stopped()

  @classmethod
  #@abstractmethod
  def host_type(clazz):
    'Host type form vmrun authentication.'
    return clazz._impl.host_type()

  @classmethod
  #@abstractmethod
  def host_type(clazz):
    'Host type form vmrun authentication.'
    return clazz._impl.host_type()

  @classmethod
  #@abstractmethod
  def preferences_filename(clazz):
    'The full path to the preferences filename.'
    return clazz._impl.preferences_filename()

  @classmethod
  #@abstractmethod
  def inventory_filename(clazz):
    'The full path to the inventory filename.'
    return clazz._impl.inventory_filename()
  
  @classmethod
  #@abstractmethod
  def vmrun_exe_path(clazz):
    'The full path to the vmrun executable.'
    return clazz._impl.vmrun_exe_path()

  @classmethod
  #@abstractmethod
  def vmrest_exe_path(clazz):
    'The full path to the vmrest executable.'
    return clazz._impl.vmrest_exe_path()
  
  @classmethod
  #@abstractmethod
  def ovftool_exe_path(clazz):
    'The full path to the ovftool executable.'
    return clazz._impl.ovftool_exe_path()
  
