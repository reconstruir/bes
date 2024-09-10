#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from abc import abstractmethod, ABCMeta

class log_writer(object, metaclass = ABCMeta):
  'Abstract base class for writing logs.'
  
  @abstractmethod
  def write(self, text):
    'same as file.write.'
    raise NotImplementedError('write')

  @abstractmethod
  def close(self):
    'same as file.close.'
    raise NotImplementedError('close')

  @abstractmethod
  def flush(self):
    'same as file.flush.'
    raise NotImplementedError('flush')
