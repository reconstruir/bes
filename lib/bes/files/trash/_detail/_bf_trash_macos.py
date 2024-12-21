#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import subprocess

from bes.system.log import logger

from ._bf_trash_i import _bf_trash_i

class _bf_trash_macos(_bf_trash_i):

  _log = logger('bf_trash')

  @classmethod
  #@abstractmethod
  def empty_trash(clazz):
    'Empty the trash.'
    cmd = [ 'osascript', '-e', 'tell app "Finder" to empty' ]
    clazz._log.log_d(f'{clazz.__name__}: emptying trash')
    subprocess.run(cmd, capture_output = True)
    clazz._log.log_d(f'{clazz.__name__}: emptied trash')
