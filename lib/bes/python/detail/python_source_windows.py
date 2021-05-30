#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path

from bes.common.check import check
from bes.fs.filename_util import filename_util
from bes.python.python_error import python_error
from bes.python.python_version import python_version
from bes.system.user import user

from .python_source_base import python_source_base

class python_source_windows(python_source_base):

  _PYTHON_DOT_ORG_DIRS = [
    r'C:\Program Files\Python37',
    r'C:\Program Files\Python38',
    r'C:\Program Files\Python39',
    r'C:\Python27',
  ]
  
  @classmethod
  #@abstractmethod
  def exe_source(clazz, exe):
    'Return the source of the python executable.  Stuff like brew, xcode, system, python.org.'
    for d in clazz._PYTHON_DOT_ORG_DIRS:
      if exe.lower().startswith(d.lower()):
        return 'python.org'
    return 'unknown'

  @classmethod
  #@abstractmethod
  def possible_python_bin_dirs(clazz):
    'Return a list of possible dirs where the python executable might be.'
    return clazz._PYTHON_DOT_ORG_DIRS

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
    if dirname.lower().startswith(user.HOME.lower()):
      return True
    return False

  @classmethod
  #@abstractmethod
  def exe_name(clazz, exe):
    'Return the name of a python exe.  without possible extensions or absolute paths.'
    basename = path.basename(exe).lower()
    if not filename_util.has_any_extension(exe, ( 'exe', 'bat', 'cmd' )):
      raise python_error('windows executable filename not valid.  should have exe, cmd or bat extension: "{}"'.format(exe))
    return filename_util.without_extension(basename)

  @classmethod
  #@abstractmethod
  def possible_python_dot_org_installer_filenames(clazz, full_version):
    'Return a list of possible python.org installer filenames for full version.'
    check.check_python_version(full_version)

    template = '{full_version}/python-{full_version}{delimiter}amd64.{extension}'
    return [ 
      template.format(full_version = full_version, extension = 'msi', delimiter = '.'),
      template.format(full_version = full_version, extension = 'exe', delimiter = '-'),
    ]

  @classmethod
  #@abstractmethod
  def virtual_env_python_exe(clazz, root_dir, version):
    'Return the absolute path the python exe in a virtual env.'
    version = python_version.check_version(version)
    return path.join(root_dir, 'Scripts', 'python.exe')

  @classmethod
  #@abstractmethod
  def virtual_env_activate_script(clazz, root_dir, variant):
    'Return the absolute path the the acitivate script of a virtual env.'
    check.check_string(root_dir)
    check.check_string(variant, allow_none = True)

    if variant == None:
      f = r'Scripts\activate.bat'
    elif variant == 'ps1':
      f = r'Scripts\Activate.ps1'
      raise python_error('unknown activate script variant: "{}"'.format(variant))
    return path.join(root_dir, f)
