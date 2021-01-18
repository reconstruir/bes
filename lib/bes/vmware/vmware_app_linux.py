#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from .vmware_app_base import vmware_app_base

from bes.system.execute import execute

class vmware_app_linux(platform_determiner_base):

  #@abstractmethod
  def is_installed(self):
    'Return True if vmware is installed.'
    raise NotImplemented('is_installed')

  #@abstractmethod
  def is_running(self):
    'Return True if vmware is running.'
    raise NotImplemented('is_running')

  #@abstractmethod
  def ensure_running(self):
    'Ensure vmware is running.'
    raise NotImplemented('ensure_running')
