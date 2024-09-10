#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from abc import abstractmethod, ABCMeta

class platform_determiner_base(object, metaclass = ABCMeta):
  'Abstract base class for determining what platform we are on.'
  
  @abstractmethod
  def system(self):
    'system.'
    pass

  @abstractmethod
  def distro(self):
    'distro.'
    pass

  @abstractmethod
  def codename(self):
    'codename.'
    pass
  
  @abstractmethod
  def family(self):
    'distro family.'
    pass

  @abstractmethod
  def version_major(self):
    'distro version major number.'
    pass

  @abstractmethod
  def version_minor(self):
    'distro version minor number.'
    pass
  
  @abstractmethod
  def arch(self):
    'arch.'
    pass
