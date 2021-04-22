#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path

from bes.fs.filename_util import filename_util
from bes.python.python_error import python_error

from .python_source_base import python_source_base

class python_source_windows(python_source_base):

  @classmethod
  #@abstractmethod
  def exe_source(self, exe):
    'Return the source of the python executable.  Stuff like brew, xcode, system, python.org.'
    return 'unknown'

  @classmethod
  #@abstractmethod
  def possible_python_bin_dirs(self):
    'Return a list of possible dirs where the python executable might be.'
    return [
      r'C:\Program Files\Python37',
      r'C:\Program Files\Python38',
      r'C:\Program Files\Python39',
      r'C:\Python27',
    ]

  @classmethod
  #@abstractmethod
  def possible_python_exe_patterns(clazz):
    'Return a list of possible python exe fnmatch patters.'
    # There are no official pythons with cmd, bat or extensions
    # but unit tests create such files to prove the api works
    return [
      'python.exe',
      'python[0-9].exe',
      'python[0-9].[0-9].exe',
      'python.cmd',
      'python[0-9].cmd',
      'python[0-9].[0-9].cmd',
      'python.bat',
      'python[0-9].bat',
      'python[0-9].[0-9].bat',
    ]

  @classmethod
  #@abstractmethod
  def possible_python_dir_should_be_ignored(clazz, dirname):
    'Return True if dirname should be ignored as a possible python bin dir.'
    if r'Microsoft\WindowsApps' in dirname:
      return True
    return False

  @classmethod
  #@abstractmethod
  def exe_name(self, exe):
    'Return the name of a python exe.  without possible extensions or absolute paths.'
    basename = path.basename(exe).lower()
    if not filename_util.has_any_extension(exe, ( 'exe', 'bat', 'cmd' )):
      raise python_error('windows executable filename not valid.  should have exe, cmd or bat extension: "{}"'.format(exe))
    return filename_util.without_extension(basename)
