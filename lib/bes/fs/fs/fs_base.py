#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from abc import abstractmethod, ABCMeta
from bes.system.compat import with_metaclass

class fs_base(with_metaclass(ABCMeta, object)):

  @abstractmethod
  def list_dir(self, d, recursive):
    'List entries in a directory.'
    pass

  @abstractmethod
  def info(self, filename):
    'Get info for a single file..'
    pass
  
  @abstractmethod
  def remove(self, filename):
    'Remove filename.'
    pass
  
  @abstractmethod
  def upload(self, filename, local_filename):
    'Upload filename from local_filename.'
    pass

  @abstractmethod
  def set_attributes(self, filename, attributes):
    'Set file attirbutes.'
    pass
  
