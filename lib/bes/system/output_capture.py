#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path
import sys
from io import StringIO
import tempfile

from .filesystem import filesystem

class output_capture(object):

  def __init__(self, binary = False):
    self._read_mode = 'rb' if binary else 'r'
    self._write_mode = 'wb' if binary else 'w'
    self._original_stdout = sys.stdout
    self._original_stderr = sys.stderr

    self._reset()
    
  @property
  def stdout(self):
    if not self._temp_stdout_filename:
      return None
    self._temp_stdout.flush()
    with open(self._temp_stdout_filename, self._read_mode) as f:
      return f.read()

  @property
  def stderr(self):
    if not self._temp_stderr_filename:
      return None
    self._temp_stderr.flush()
    with open(self._temp_stderr_filename, self._read_mode) as f:
      return f.read()
  
  def __enter__(self):
    self._temp_stdout_filename = tempfile.NamedTemporaryFile(prefix = 'stdout-',
                                                             suffix = '-capture',
                                                             delete = True).name
    self._temp_stderr_filename = tempfile.NamedTemporaryFile(prefix = 'stderr-',
                                                             suffix = '-capture',
                                                             delete = True).name
    self._temp_stdout = open(self._temp_stdout_filename, self._write_mode)
    self._temp_stderr = open(self._temp_stderr_filename, self._write_mode)
    sys.stdout = self._temp_stdout
    sys.stderr = self._temp_stderr
    return self
  
  def __exit__(self, type, value, traceback):
    sys.stdout = self._original_stdout
    sys.stderr = self._original_stderr
    self._temp_stdout.flush()
    self._temp_stderr.flush()
    self._temp_stdout.close()
    self._temp_stderr.close()
    filesystem.remove(self._temp_stdout_filename)
    filesystem.remove(self._temp_stderr_filename)
    self._reset()

  def _reset(self):
    self._temp_stdout_filename = None
    self._temp_stdout_filename = None
    self._temp_stdout = None
    self._temp_stderr = None
    
