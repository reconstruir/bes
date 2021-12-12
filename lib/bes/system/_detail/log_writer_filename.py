#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from .log_writer import log_writer

class log_writer_filename(log_writer):
  'log writer to file given by filename and managed internally.'

  def __init__(self, filename):
    self.filename = filename
    self._fp = open(self._resolve_filename(self.filename), 'a')

  @classmethod
  def _resolve_filename(clazz, filename):
    'resolve env vars and ~ in a filename.'
    return path.expandvars(path.expanduser(filename))
    
  #@abstractmethod
  def write(self, text):
    'same as file.write.'
    assert self._fp
    self._fp.write(text)

  #@abstractmethod
  def close(self):
    'same as file.close.'
    assert self._fp
    self._fp.close()
    self._fp = None
    
  #@abstractmethod
  def flush(self):
    'same as file.flush.'
    assert self._fp
    self._fp.flush()
