#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from .log_writer_file_object import log_writer_file_object
from .log_writer_filename import log_writer_filename
from .log_writer_stdout import log_writer_stdout

from bes.system.compat import compat

class log_writer_list(object):
  'a list of log writers that all get written to.'

  def __init__(self):
    self._writers = []
    self.add_stdout()
  
  def write(self, text):
    'same as file.write.'
    for writer in self._writers:
      writer.write(text)

  def close(self):
    'same as file.close.'
    for writer in self._writers:
      writer.close()
  
  def flush(self):
    'same as file.flush.'
    for writer in self._writers:
      writer.flush()

  def clear(self):
    'close and remove all the writers.'
    self.close()
    self._writers = []

  def reset(self):
    'reset to defaults.'
    self.clear()
    self.add_stdout()

  def add_stdout(self):
    'add a writer to stdout.'
    for writer in self._writers:
      if isinstance(writer, log_writer_stdout):
        return
    writer = log_writer_stdout()
    self._writers.append(writer)
    
  def add_filename(self, filename):
    'add a writer to a filename.'
    for writer in self._writers:
      if isinstance(writer, log_writer_filename) and writer.filename == filename:
        return
    writer = log_writer_filename(filename)
    self._writers.append(writer)

  def add_file_object(self, file_object):
    'add a writer to a user manager file object.'
    if not compat.is_file(file_object):
      raise ValueError('file_object is not a file.')
      
    writer = log_writer_file_object(file_object)
    self._writers.append(writer)

  def configure(self, value):
    'configure logging.'
    command, sep, arg = value.partition(':')
    
    if command == 'reset':
      self.reset()
    elif command == 'clear':
      self.clear()
    elif command in [ 'file' ]:
      self.add_filename(arg)
    elif command in [ 'stdout' ]:
      self.add_stdout(arg)
    else:
      raise ValueError('invalid log configuration: "{}"'.format(value))
