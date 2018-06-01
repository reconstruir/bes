#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import multiprocessing, os.path as path, os, shutil, tempfile
from abc import abstractmethod, ABCMeta
from bes.common import check
from bes.system import log
from bes.thread.decorators import synchronized_method
from bes.system.compat import with_metaclass

from .file_util import file_util

from ._detail.trash_detail import fast_deleter, trash_process

class file_trash(object):

  def __init__(self, location, deleter = None):
    log.add_logging(self)
    self._location = location
    file_util.mkdir(self._location)
    self._location_device_id = self._device_id(self._location)
    self.trash_process = trash_process(self._location, deleter or fast_deleter())
    self.trash_process.start()
    
  def trash(clazz, what):
    check.check_string(what)
    self.trash_process.trash(what)
    
  @classmethod
  def _valid_type(clazz, p):
    return path.isfile(p) or path.isdir(p) or path.islink(p)
                  
  @classmethod
  def _device_id(clazz, p):
    return os.stat(p).st_dev

  def start(self):
    self.trash_process.start()
  
  def stop(self):
    self.trash_process.stop()
