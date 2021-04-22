#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from abc import abstractmethod, ABCMeta
from bes.system.compat import with_metaclass
from bes.system.user import user

class python_source_unix(with_metaclass(ABCMeta, object)):
  '''
  Abstract interface for dealing with the source of a python exe
  and other platform specific python information
  '''

  @classmethod
  #@abstractmethod
  def possible_python_exe_patterns(clazz):
    'Return a list of possible python exe fnmatch patters.'
    return [
      'python',
      'python[0-9]',
      'python[0-9].[0-9]',
    ]

  @classmethod
  #@abstractmethod
  def possible_python_dir_should_be_ignored(clazz, dirname):
    'Return True if dirname should be ignored as a possible python bin dir.'
    if dirname.startswith(user.HOME):
      return True
    return False

  @classmethod
  def _source_is_unix_system(clazz, exe):
    'Return True if the given python executable came builtin to the current system'
    return exe.lower().startswith('/usr/bin/python')
