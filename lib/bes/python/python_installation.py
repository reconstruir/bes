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
