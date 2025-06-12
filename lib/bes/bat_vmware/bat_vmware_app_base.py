#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from abc import abstractmethod, ABCMeta

class bat_vmware_app_base(object, metaclass = ABCMeta):
  'Abstract interface for interacting with the vmware workstation or fusion main application.'

  @classmethod
  @abstractmethod
  def install_path(clazz):
    'The full path to where vmware is installed.'
    raise NotImplementedError('install_path')

  @classmethod
  @abstractmethod
  def is_installed(clazz):
    'Return True if vmware is installed.'
    raise NotImplementedError('is_installed')

  @classmethod
  @abstractmethod
  def is_running(clazz):
    'Return True if vmware is running.'
    raise NotImplementedError('is_running')

  @classmethod
  @abstractmethod
  def ensure_running(clazz):
    'Ensure vmware is running.'
    raise NotImplementedError('ensure_running')

  @classmethod
  @abstractmethod
  def ensure_stopped(clazz):
    'Ensure vmware is stopped.'
    raise NotImplementedError('ensure_stopped')

  @classmethod
  @abstractmethod
  def host_type(clazz):
    'Host type form vmrun authentication.'
    raise NotImplementedError('host_type')

  @classmethod
  @abstractmethod
  def preferences_filename(clazz):
    'The full path to the preferences filename.'
    raise NotImplementedError('preferences_filename')

  @classmethod
  @abstractmethod
  def inventory_filename(clazz):
    'The full path to the inventory filename.'
    raise NotImplementedError('inventory_filename')
  
  @classmethod
  @abstractmethod
  def vmrun_exe_path(clazz):
    'The full path to the vmrun executable.'
    raise NotImplementedError('vmrun_exe_path')

  @classmethod
  @abstractmethod
  def vmrest_exe_path(clazz):
    'The full path to the vmrest executable.'
    raise NotImplementedError('vmrest_exe_path')
  
  @classmethod
  @abstractmethod
  def ovftool_exe_path(clazz):
    'The full path to the ovftool executable.'
    raise NotImplementedError('ovftool_exe_path')
  
