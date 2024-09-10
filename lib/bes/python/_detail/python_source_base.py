#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from abc import abstractmethod, ABCMeta

class python_source_base(object, metaclass = ABCMeta):
  '''
  Abstract interface for dealing with the source of a python exe
  and other platform specific python information
  '''

  @classmethod
  @abstractmethod
  def exe_source(clazz, exe):
    'Return the source of the python executable.  Stuff like brew, xcode, system, python.org.'
    raise NotImplemented('exe_source')

  @classmethod
  @abstractmethod
  def possible_python_bin_dirs(clazz):
    'Return a list of possible dirs where the python executable might be.'
    raise NotImplemented('possible_python_bin_dirs')

  @classmethod
  @abstractmethod
  def possible_python_exe_patterns(clazz):
    'Return a list of possible python exe fnmatch patters.'
    raise NotImplemented('possible_python_exe_patterns')

  @classmethod
  @abstractmethod
  def possible_python_dir_should_be_ignored(clazz, dirname):
    'Return True if dirname should be ignored as a possible python bin dir.'
    raise NotImplemented('possible_python_dir_should_be_ignored')

  @classmethod
  @abstractmethod
  def exe_name(clazz, exe):
    'Return the name of a python exe.  without possible extensions or absolute paths.'
    raise NotImplemented('exe_name')

  @classmethod
  @abstractmethod
  def possible_python_dot_org_installer_filenames(clazz, full_version):
    'Return a list of possible python.org installer filenames for full version.'
    raise NotImplemented('possible_python_dot_org_installer_filenames')

  @classmethod
  @abstractmethod
  def versioned_python_exe(clazz, root_dir, version):
    'Return the absolute path the python exe with major.minor version in a virtual env.'
    raise NotImplemented('versioned_python_exe')

  @classmethod
  @abstractmethod
  def python_exe(clazz, root_dir, version):
    'Return the absolute path the python exe with major version in a virtual env.'
    raise NotImplemented('python_exe')
  
  @classmethod
  @abstractmethod
  def activate_script(clazz, root_dir, variant):
    'Return the absolute path the the acitivate script of a virtual env.'
    raise NotImplemented('activate_script')
