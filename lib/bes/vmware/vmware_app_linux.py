#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from .vmware_app_base import vmware_app_base

from bes.system.which import which
from bes.system.execute import execute

class vmware_app_linux(vmware_app_base):

  @classmethod
  #@abstractmethod
  def is_installed(self):
    'Return True if vmware is installed.'
    raise NotImplemented('is_installed')

  @classmethod
  #@abstractmethod
  def is_running(self):
    'Return True if vmware is running.'
    raise NotImplemented('is_running')

  @classmethod
  #@abstractmethod
  def ensure_running(self):
    'Ensure vmware is running.'
    raise NotImplemented('ensure_running')

  @classmethod
  #@abstractmethod
  def ensure_stopped(self):
    'Ensure vmware is stopped.'
    raise NotImplemented('ensure_stopped')

  @classmethod
  #@abstractmethod
  def host_type(self):
    'Host type form vmrun authentication.'
    return 'ws'
  
  @classmethod
  #@abstractmethod
  def preferences_filename(self):
    'The full path to the preferneces filename.'
    return '/etc/vmware/config'

  @classmethod
  #@abstractmethod
  def vmrun_exe_path(clazz):
    'The full path to the vmrun executable.'
    return which.which('vmrun')
