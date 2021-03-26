#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from bes.common.check import check
from bes.property.cached_property import cached_property
from bes.system.host import host
from bes.system.log import logger
from bes.system.os_env import os_env
from bes.fs.file_mime import file_mime
from bes.fs.filename_util import filename_util

from .python_error import python_error

class python_installation(object):
  'Class to determine the filename and directory values of a pip installatiuon.'

  _log = logger('pip')
  
  def __init__(self, root_dir, python_version, system = None):
    check.check_string(root_dir)
    check.check_string(python_version)

    self._root_dir = root_dir
    self._python_version = python_version
    self._system = system or host.SYSTEM

  @cached_property
  def pip_exe(self):
    'Return the pip executable'
    if self._system == host.WINDOWS:
      pip_exe_basename = 'pip{}.exe'.format(self._python_version)
      python_dir = 'Python{}'.format(self._python_version.replace('.', ''))
      if self._python_version == '2.7':
        pexe = path.join(self._root_dir, 'Scripts', pip_exe_basename)
      else:
        pexe = path.join(self._root_dir, python_dir, 'Scripts', pip_exe_basename)
    elif self._system in ( host.LINUX, host.MACOS ):
      pip_exe_basename = 'pip{}'.format(self._python_version)
      pexe = path.join(self._root_dir, 'bin', pip_exe_basename)
    else:
      host.raise_unsupported_system()
    return pexe
    
    return self._pip_exe

  @cached_property
  def bin_dir(self):
    'Return the bin dir'
    if self._system == host.WINDOWS:
      python_dir = 'Python{}'.format(self._python_version.replace('.', ''))
      if self._python_version == '2.7':
        bin_dir = path.join(self._root_dir, 'Scripts')
      else:
        bin_dir = path.join(self._root_dir, python_dir, 'Scripts')
    elif self._system in ( host.LINUX, host.MACOS ):
      bin_dir = path.join(self._root_dir, 'bin')
    else:
      host.raise_unsupported_system()
    return bin_dir
  
  @cached_property
  def site_packages_dir(self):
    'Return the pip site-packages dir sometimes needed for PYTHONPATH'
    if self._system == host.WINDOWS:
      python_dir = 'Python{}'.format(self._python_version.replace('.', ''))
      site_packaged_dir = path.join(self._root_dir, python_dir, 'site-packages')
    elif self._system in ( host.LINUX, host.MACOS ):
      site_packaged_dir = path.join(self._root_dir, 'lib/python/site-packages')
    else:
      host.raise_unsupported_system()
    return site_packaged_dir

  @cached_property
  def PYTHONPATH(self):
    return [ self.site_packages_dir ]

  @cached_property
  def PATH(self):
    return [ self.bin_dir ]
  
  @classmethod
  def find_root_dir(clazz, pip_exe, system = None):
    'Find the install dir from the pip exe'
    check.check_string(pip_exe)

    if self._system == host.WINDOWS:
      result = self._find_root_dir_windows(pip_exe)
    elif self._system in ( host.LINUX, host.MACOS ):
      result = self._find_root_dir_unix(pip_exe)
    else:
      host.raise_unsupported_system()
    return result

  @classmethod
  def _find_root_dir_unix(clazz, pip_exe):
    return path.normpath(path.join(path.dirname(pip_exe), '..'))
  
  @classmethod
  def _find_root_dir_windows(clazz, pip_exe):
    basename = path.basename(pip_exe)

    f = re.findall(r'^pip(\d+\.\d+)\....$', basename, flags = re.IGNORECASE)
    if not f:
      raise python_error('pip_exe does not contain a python version: "{}"'.format(pip_exe))
    if len(f) != 1:
      raise python_error('pip_exe does not contain a python version: "{}"'.format(pip_exe))
    python_version = f[0]
    parent_dir = file_path.parent_dir(pip_exe)

    if python_version == '2.7':
      result = file_path.parent_dir(parent_dir)
    else:
      result = file_path.parent_dir(parent_dir)
      
    
    return 'caca'
    root_dir = path.dirname(pip_exe)
    lib_dir = path.normpath(path.join(path.join(root_dir, path.pardir), 'lib'))
    possible_python_libdirs = file_path.glob(lib_dir, 'python*')
    num_possible_python_libdirs = len(possible_python_libdirs)
    if num_possible_python_libdirs == 1:
      python_libdir = possible_python_libdirs[0]
    else:
      python_libdir = None
    if not python_libdir:
      return None
    if not python_libdir:
      return None
    possible_site_packages_dir = path.join(python_libdir, 'site-packages')
    if path.isdir(possible_site_packages_dir):
      return possible_site_packages_dir
    return None
  
