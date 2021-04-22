#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from .detail.python_source_base import python_source_base

from bes.system.host import host

class python_source(python_source_base):

  def _find_impl_class():
    result = None
    if host.is_linux():
      from .detail.python_source_linux import python_source_linux
      result = python_source_linux
    elif host.is_macos():
      from .detail.python_source_macos import python_source_macos
      result = python_source_macos
    elif host.is_windows():
      from .detail.python_source_windows import python_source_windows
      result = python_source_windows
    return result
  
  _impl_class = _find_impl_class()
  if not _impl_class:
    host.raise_unsupported_system()
  
  @classmethod
  #@abstractmethod
  def exe_source(clazz, exe):
    'Return the source of the python executable.  Stuff like brew, xcode, system, python.org.'
    return clazz._impl_class.exe_source(exe)

  @classmethod
  #@abstractmethod
  def possible_python_bin_dirs(clazz):
    'Return a list of possible dirs where the python executable might be.'
    return clazz._impl_class.possible_python_bin_dirs()

  @classmethod
  #@abstractmethod
  def possible_python_exe_patterns(clazz):
    'Return a list of possible python exe fnmatch patters.'
    return clazz._impl_class.possible_python_exe_patterns()

  @classmethod
  #@abstractmethod
  def possible_python_dir_should_be_ignored(clazz, dirname):
    'Return True if dirname should be ignored as a possible python bin dir.'
    return clazz._impl_class.possible_python_dir_should_be_ignored(dirname)
