#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from abc import abstractmethod, ABCMeta
from bes.system.compat import with_metaclass

class fs_base(with_metaclass(ABCMeta, object)):

  @abstractmethod
  def name(self):
    'The name if this fs.'
    pass

  @abstractmethod
  def list_dir(self, d, recursive):
    'List entries in a directory.'
    pass

  @abstractmethod
  def file_info(self, filename):
    'Get info for a single file..'
    pass
  
  @abstractmethod
  def remove_file(self, filename):
    'Remove filename.'
    pass
  
  @abstractmethod
  def upload_file(self, filename, local_filename):
    'Upload filename from local_filename.'
    pass

  @abstractmethod
  def set_file_attributes(self, filename, attributes):
    'Set file attirbutes.'
    pass
  
