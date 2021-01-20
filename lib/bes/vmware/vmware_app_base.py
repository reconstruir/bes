#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from abc import abstractmethod, ABCMeta
from bes.system.compat import with_metaclass

class vmware_app_base(with_metaclass(ABCMeta, object)):
  'Abstract interface for interacting with the vmware workstation or fusion main application.'
  
  @abstractmethod
  def is_installed(self):
    'Return True if vmware is installed.'
    raise NotImplemented('is_installed')

  @abstractmethod
  def is_running(self):
    'Return True if vmware is running.'
    raise NotImplemented('is_running')

  @abstractmethod
  def ensure_running(self):
    'Ensure vmware is running.'
    raise NotImplemented('ensure_running')

  @abstractmethod
  def ensure_stopped(self):
    'Ensure vmware is stopped.'
    raise NotImplemented('ensure_stopped')

  #@abstractmethod
  def host_type(self):
    'Host type form vmrun authentication.'
    raise NotImplemented('host_type')
  
