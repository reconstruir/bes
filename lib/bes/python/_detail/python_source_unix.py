#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path

from abc import abstractmethod, ABCMeta

from bes.python.python_error import python_error
from bes.python.python_version import python_version
from bes.system.check import check
from bes.system.environment import environment

class python_source_unix(object, metaclass = ABCMeta):
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
      'python[0-9].[0-9][0-9]',
    ]

  @classmethod
  #@abstractmethod
  def possible_python_dir_should_be_ignored(clazz, dirname):
    'Return True if dirname should be ignored as a possible python bin dir.'
    if dirname.startswith(environment.home_dir()):
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
  def versioned_python_exe(clazz, root_dir, version):
    'Return the absolute path the python exe with major.minor version in a virtual env.'
    version = python_version.check_version(version)
    version_exe_basename = 'python{}'.format(str(version))
    exe = path.join(root_dir, 'bin', version_exe_basename)
    return exe

  @classmethod
  #@abstractmethod
  def python_exe(clazz, root_dir, version):
    'Return the absolute path the python exe with major version in a virtual env.'
    version = python_version.check_version(version)
    major_version_exe_basename = 'python{}'.format(str(version.major_version))
    exe = path.join(root_dir, 'bin', major_version_exe_basename)
    return exe
  
  @classmethod
  #@abstractmethod
  def activate_script(clazz, root_dir, variant):
    'Return the absolute path the the acitivate script of a virtual env.'
    check.check_string(root_dir)
    check.check_string(variant, allow_none = True)

    if variant == None:
      f = 'bin/activate'
    elif variant == 'fish':
      f = 'bin/activate.fish'
    elif variant == 'csh':
      f = 'bin/activate.csh'
    else:
      raise python_error('unknown activate script variant: "{}"'.format(variant))
    return path.join(root_dir, f)
