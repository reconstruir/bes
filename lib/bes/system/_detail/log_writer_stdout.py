#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import sys
from .log_writer import log_writer

class log_writer_stdout(log_writer):
  'log writer to stdout.'

  def __init__(self):
    pass
  
  #@abstractmethod
  def write(self, text):
    'same as file.write.'
    sys.stdout.write(text)

  #@abstractmethod
  def close(self):
    'same as file.close.'
    pass
  
  #@abstractmethod
  def flush(self):
    'same as file.flush.'
    sys.stdout.flush()
