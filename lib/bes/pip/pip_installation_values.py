#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

#from collections import namedtuple
#import json
from os import path
#
from bes.common.check import check
#
#from bes.fs.dir_util import dir_util
#from bes.fs.file_find import file_find
#from bes.fs.file_util import file_util
#from bes.system.execute import execute
from bes.system.host import host
from bes.property.cached_property import cached_property
from bes.system.log import logger
from bes.system.os_env import os_env
#from bes.url.url_util import url_util
#
#from bes.python.python_exe import python_exe
#from bes.python.python_version import python_version
#
#from .pip_error import pip_error
#from .pip_exe import pip_exe
#from .pip_installer_options import pip_installer_options
#
class pip_installation_values(object):
  'Class to determine the filename and directory values of a pip installatiuon.'

  _log = logger('pip')
  
  def __init__(self, install_dir, python_version, system = None):
    check.check_string(install_dir)
    check.check_string(python_version)

    self._install_dir = install_dir
    self._python_version = python_version
    self._system = system or host.SYSTEM

  @cached_property
  def pip_exe(self):
    'Return the pip executable'
    if self._system == host.WINDOWS:
      pip_exe_basename = 'pip{}.exe'.format(self._python_version)
      python_dir = 'Python{}'.format(self._python_version.replace('.', ''))
      if self._python_version == '2.7':
        pexe = path.join(self._install_dir, 'Scripts', pip_exe_basename)
      else:
        pexe = path.join(self._install_dir, python_dir, 'Scripts', pip_exe_basename)
    elif self._system in ( host.LINUX, host.MACOS ):
      pip_exe_basename = 'pip{}'.format(self._python_version)
      pexe = path.join(self._install_dir, 'bin', pip_exe_basename)
    else:
      host.raise_unsupported_system()
    return pexe
    
    return self._pip_exe

  @cached_property
  def site_packages_dir(self):
    'Return the pip site-packages dir sometimes needed for PYTHONPATH'
    if self._system == host.WINDOWS:
      python_dir = 'Python{}'.format(self._python_version.replace('.', ''))
      #if self._python_version == '2.7':
      #  site_packaged_dir = path.join(self._install_dir, 'site-packages')
      #else:
      site_packaged_dir = path.join(self._install_dir, python_dir, 'site-packages')
    elif self._system in ( host.LINUX, host.MACOS ):
      site_packaged_dir = path.join(self._install_dir, 'lib/python/site-packages')
    else:
      host.raise_unsupported_system()
    return site_packaged_dir

  @cached_property
  def pip_env(self):
    'Make a clean environment for python or pip'
    extra_env = {
      'PYTHONUSERBASE': self._install_dir,
      'PYTHONPATH': self.site_packages_dir,
    }
    return os_env.make_clean_env(update = extra_env)
