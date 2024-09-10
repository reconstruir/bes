#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path, os, shutil, tempfile
from abc import abstractmethod, ABCMeta
from ..system.check import check
from bes.system.log import log
from bes.thread.decorators import synchronized_method

from .file_util import file_util

from ._detail.trash_detail import fast_deleter, trash_process

class file_trash(object):

  DEFAULT_NICENESS = 0
  DEFAULT_TIMEOUT = 0.500
  
  def __init__(self, location, niceness_level = None, timeout = None, deleter = None):
    log.add_logging(self, 'file_trash')
    niceness_level = niceness_level or self.DEFAULT_NICENESS
    timeout = timeout or self.DEFAULT_TIMEOUT
    deleter = deleter or fast_deleter()
    file_util.mkdir(location)
    assert path.isdir(location)
    self._location = location
    self._location_device_id = file_util.device_id(self._location)
    self.trash_process = trash_process(self._location, niceness_level, timeout, deleter)
    
  def trash(self, what):
    check.check_string(what)
    if not self._valid_type(what):
      raise RuntimeError('Invalid file type: %s' % (what))
    if file_util.device_id(what) != self._location_device_id:
      raise RuntimeError('%s is not in the save filesystem as %s' % (what, self._location))
    self.trash_process.trash(what)
    
  @classmethod
  def _valid_type(clazz, p):
    return path.isfile(p) or path.isdir(p) or path.islink(p)
                  
  def start(self):
    self.trash_process.start()
  
  def stop(self):
    self.trash_process.stop()
