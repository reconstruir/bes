#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path, os, shutil, tempfile
from multiprocessing import Lock, Queue, Process
from abc import abstractmethod, ABCMeta
from bes.system.check import check
from bes.system.log import log
from bes.fs.dir_util import dir_util
from bes.thread.decorators import synchronized_method

from bes.fs.file_util import file_util

class deleter(object, metaclass = ABCMeta):
  
  @abstractmethod
  def delete_file(self, filename):
    'Delete a file or directory.'
    raise NotImplementedError('not implemented')

class fast_deleter(deleter):

  def __init__(self):
    log.add_logging(self, 'fast_deleter')
  
  #@abstractmethod
  def delete_file(self, filename):
    'Delete a file or directory.'
    self.log_i('deleting %s' % (filename))
    file_util.remove(filename)

class slow_deleter(deleter):
  'Delete files slowly by sleeping between deletes for files in directories.'
  
  def __init__(self, sleep_time):
    log.add_logging(self, 'slow_deleter')
    self._sleep_time = sleep_time
  
  #@abstractmethod
  def delete_file(self, filename):
    'Delete a file or directory.'
    if path.isfile(filename):
      self.log_i('deleting single file %s' % (filename))
      file_util.remove(filename)
    elif path.isdir(filename):
      files = dir_util.list(filename)
      self.log_i('deleting many files: %s' % (files))
      for f in files:
        self.log_i('deleting next file %s' % (f))
        file_util.remove(f)
        self.log_i('sleeping for %f seconds' % (self._sleep_time))
        time.sleep(self._sleep_time)
    else:
      raise RuntimeError('invalid file type: %s' % (filename))

class trash_process(object):

  TERMINATE = { 'command': 'terminate' }
  WAKE_UP = { 'command': 'wakeup' }
  
  def __init__(self, location, niceness_level, timeout, deleter):
    log.add_logging(self, 'trash_process')
    self.log_i('trash_process init with location=%s niceness_level=%s timeout=%s' % (location, niceness_level, timeout))
    assert path.isdir(location)
    self._location = location
    self._niceness_level = niceness_level
    self._timeout = timeout
    self._location_lock = Lock()
    self._process = None
    self._queue = Queue()
    
  def _process_main(self, location, niceness_level, timeout):
    #os.nice(20)
    terminated = False
    self.log_i('trash process starts')
    while True:
      if terminated:
        break
      self._delete_one()
      try:
        payload = self._queue.get(timeout = timeout)
        check.check_dict(payload)
        command = payload['command']
        if command == 'terminate':
          self.log_i('got terminate command')
          terminated = True
        elif command == 'wakeup':
          self.log_i('got wakeup command')
          pass
      except Queue.Empty as ex:
        self.log_d('caught Queue.Empty exception')
        pass
    self.log_i('trash process ends')
    return 0

  @synchronized_method('_location_lock')
  def _list_trash(self):
    if not path.isdir(self._location):
      print('WARNING: location disappeared: %s' % (self._location))
      return []
    return dir_util.list(self._location)

  @synchronized_method('_location_lock')
  def trash(self, what):
    self.log_i('trash(what %s)' % (what))
    trash_path = tempfile.mkdtemp(prefix = path.basename(what) + '.', dir = self._location)
    shutil.move(what, trash_path)
    self.log_i('trash() move %s to %s' % (what, trash_path))
    self._queue.put(self.WAKE_UP)
  
  def _delete_one(self):
    files = self._list_trash()
    self.log_i('_delete_one(files = %s)' % (files))
    if not files:
      return False
    to_delete = files.pop(0)
    file_util.remove(to_delete)
    return len(files) > 0
    
  def start(self):
    self.log_i('start()')
    if self._process:
      raise RuntimeError('process already started.')
    args = ( self._location, self._niceness_level, self._timeout )
    self._process = Process(name = 'deleter', target = self._process_main, args = args)
    # Daemonize it so that if the user never calls stop() the parent process can stil process exit
    self._process.daemon = True
    self._process.start()
  
  def stop(self):
    self.log_i('stop()')
    if not self._process:
      raise RuntimeError('process not started.')
    self._queue.put(self.TERMINATE)
    self._process.join()
    #self._process.terminate()
    self._process = None
