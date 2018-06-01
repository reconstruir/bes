#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import multiprocessing, os.path as path, os, shutil, tempfile
from abc import abstractmethod, ABCMeta
from bes.common import check
from bes.system import log
from bes.fs import dir_util
from bes.thread.decorators import synchronized_method
from bes.system.compat import with_metaclass

from bes.fs import file_util

class deleter(with_metaclass(ABCMeta, object)):

  @abstractmethod
  def delete_file(self, filename):
    'Delete a file or directory.'
    raise NotImplementedError('not implemented')

class fast_deleter(deleter):

  #@abstractmethod
  def delete_file(self, filename):
    'Delete a file or directory.'
    file_util.remove(filename)

class slow_deleter(deleter):
  'Delete files slowly by sleeping between deletes for files in directories.'
  
  def __init__(self, sleep_time):
    self._sleep_time = sleep_time
  
  #@abstractmethod
  def delete_file(self, filename):
    'Delete a file or directory.'
    if path.isfile(filename):
      file_util.remove(filename)
    elif path.isdir(filename):
      files = dir_util.list(filename)
      for f in files:
        file_util.remove(f)
        time.sleep(self._sleep_time)
    else:
      raise RuntimeError('invalid file type: %s' % (filename))

class trash_process(object):

  class terminate(object):
    pass
  
  def __init__(self, location, deleter):
    log.add_logging(self)
    self._location = location
    self._location_lock = multiprocessing.Lock()
    self._process = None
    self._queue = multiprocessing.Queue()
    
  def _process_main(self, location, niceness_level):
    #os.nice(20)
    terminated = False
    while True:
      if terminated:
        break
      self._delete_one()
      try:
        what = self._queue.get(timeout = 0.500)
        if isinstance(what, self.terminated):
          terminated = True
      except multiprocessing.Queue.Empty as ex:
        pass
    return 0

  @synchronized_method('_location_lock')
  def _list_trash(self):
    assert path.isdir(self._location)
    return dir_util.list(self._location)

  @synchronized_method('_location_lock')
  def trash(self, what):
    trash_path = tempfile.mkdtemp(prefix = path.basename(what) + '.', dir = self._location)
    shutil.move(what, trash_path)
    self._queue.put(None)
  
  def _delete_one(self):
    files = self._list_trash()
    if not files:
      return False
    to_delete = files.pop(0)
    file_util.remove(to_delete)
    return len(files) > 0
    
  def start(self):
    self.log_i('start()')
    if self._process:
      raise RuntimeError('process already started.')
    self._process = multiprocessing.Process(name = 'deleter', target = self._process_main, args=('bob',))
#    self._process.daemon = True
    self._process.start()
  
  def stop(self):
    self.log_i('stop()')
    if not self._process:
      raise RuntimeError('process not started.')
    self._queue.put(self.terminate())
    self._process.join()
    #self._process.terminate()
    self._process = None
