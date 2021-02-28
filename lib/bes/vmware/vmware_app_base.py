#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from abc import abstractmethod, ABCMeta
from bes.system.compat import with_metaclass

class vmware_app_base(with_metaclass(ABCMeta, object)):
  'Abstract interface for interacting with the vmware workstation or fusion main application.'
  
  @classmethod
  @abstractmethod
  def is_installed(clazz):
    'Return True if vmware is installed.'
    raise NotImplemented('is_installed')

  @classmethod
  @abstractmethod
  def is_running(clazz):
    'Return True if vmware is running.'
    raise NotImplemented('is_running')

  @classmethod
  @abstractmethod
  def ensure_running(clazz):
    'Ensure vmware is running.'
    raise NotImplemented('ensure_running')

  @classmethod
  @abstractmethod
  def ensure_stopped(clazz):
    'Ensure vmware is stopped.'
    raise NotImplemented('ensure_stopped')

  @classmethod
  @abstractmethod
  def host_type(clazz):
    'Host type form vmrun authentication.'
    raise NotImplemented('host_type')

  @classmethod
  @abstractmethod
  def preferences_filename(clazz):
    'The full path to the preferneces filename.'
    raise NotImplemented('preferences_filename')

  @classmethod
  @abstractmethod
  def vmrun_exe_path(clazz):
    'The full path to the vmrun executable.'
    raise NotImplemented('vmrun_exe_path')
