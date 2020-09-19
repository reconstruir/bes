#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from .log_writer import log_writer

class log_writer_file_object(log_writer):
  'log writer to an already open file object managed by the user.'

  def __init__(self, fp):
    assert self._fp
    self._fp = fp

  #@abstractmethod
  def write(self, text):
    'same as file.write.'
    assert self._fp
    self._fp.write(text)

  #@abstractmethod
  def close(self):
    'same as file.close.'
    self._fp = fp
    
  #@abstractmethod
  def flush(self):
    'same as file.flush.'
    assert self._fp
    self._fp.flush()
