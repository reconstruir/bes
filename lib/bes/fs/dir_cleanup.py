#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path

from bes.fs.dir_util import dir_util
from bes.fs.file_util import file_util

class dir_cleanup(object):
  '''
  A context manager to cleanup a directory.  An files that exist
  between enter and exit are removed.
  '''
  
  def __init__(self, where):
    self._where = where
    self._before = None
    
  def __enter__(self):
    if not path.isdir(self._where):
      raise IOError('Directory not found: "{}"'.format(self._where))
    self._before = set(dir_util.list(self._where))
    return self
  
  def __exit__(self, type, value, traceback):
    if not path.isdir(self._where):
      raise IOError('Directory not found: "{}"'.format(self._where))
    after = set(dir_util.list(self._where))
    diff = after - self._before
    if diff:
      file_util.remove(list(diff))
