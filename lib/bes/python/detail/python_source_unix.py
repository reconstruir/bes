#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path

from abc import abstractmethod, ABCMeta
from bes.python.python_version import python_version
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

  @classmethod
  #@abstractmethod
  def exe_name(clazz, exe):
    'Return the name of a python exe.  without possible extensions or absolute paths.'
    return path.basename(exe)

  @classmethod
  #@abstractmethod
  def virtual_env_python_exe(clazz, root_dir, version):
    'Return the absolute path the python exe in a virtual env.'
    version = python_version.check_version(version)

    exe_basename = 'python{}'.format(version)
    return path.join(root_dir, 'bin', exe_basename)
