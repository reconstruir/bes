#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import sys
from io import StringIO

class output_capture(object):

  def __init__(self):
    self._original_stdout = sys.stdout
    self._original_stderr = sys.stderr
    self._stdout_buffer = StringIO()
    self._stderr_buffer = StringIO()

  @property
  def stdout(self):
    return self._stdout_buffer.getvalue()

  @property
  def stderr(self):
    return self._stderr_buffer.getvalue()
  
  def __enter__(self):
    sys.stdout = self._stdout_buffer
    sys.stderr = self._stderr_buffer
    return self
  
  def __exit__(self, type, value, traceback):
    sys.stdout = self._original_stdout
    sys.stderr = self._original_stderr
