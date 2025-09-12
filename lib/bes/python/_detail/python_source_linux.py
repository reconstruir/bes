#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from .python_source_unix import python_source_unix

class python_source_linux(python_source_unix):

  @classmethod
  #@abstractmethod
  def exe_source(clazz, exe):
    'Return the source of the python executable.  Stuff like brew, xcode, system, python.org.'
    if clazz._source_is_unix_system(exe):
      return 'system'
    else:
      return 'unknown'

  @classmethod
  #@abstractmethod
  def possible_python_bin_dirs(clazz):
    'Return a list of possible dirs where the python executable might be.'
    return [
      '/usr/bin',
      '/usr/local/bin',
      '/opt/local/bin',
    ]
  
  @classmethod
  #@abstractmethod
  def possible_python_dot_org_installer_filenames(clazz):
    'Return a list of possible python.org installer filenames.'
    raise NotImplementedError('possible_python_dot_org_installer_filenames')
