#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path, os, shutil, tempfile
from multiprocessing import Lock, Queue, Process
from Queue import Empty as QueueEmpty
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

  TERMINATE = { 'command': 'terminate' }
  WAKE_UP = { 'command': 'wakeup' }
  
  def __init__(self, location, niceness_level, deleter):
    log.add_logging(self)
    self._location = location
    self._niceness_level = niceness_level
    self._location_lock = Lock()
    self._process = None
    self._queue = Queue()
    
  def _process_main(self, location, niceness_level):
    #os.nice(20)
    terminated = False
    while True:
      if terminated:
        break
      self._delete_one()
      try:
        payload = self._queue.get(timeout = 0.500)
        check.check_dict(payload)
        command = payload['command']
        if command == 'terminate':
          terminated = True
        elif command == 'wakeup':
          pass
      except QueueEmpty as ex:
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
    self._queue.put(self.WAKE_UP)
  
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
    args = ( self._location, self._niceness_level )
    self._process = Process(name = 'deleter', target = self._process_main, args = args)
#    self._process.daemon = True
    self._process.start()
  
  def stop(self):
    self.log_i('stop()')
    if not self._process:
      raise RuntimeError('process not started.')
    self._queue.put(self.TERMINATE)
    self._process.join()
    #self._process.terminate()
    self._process = None
