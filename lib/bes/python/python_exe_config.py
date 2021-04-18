#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from bes.common.check import check
from bes.system.log import logger
from bes.system.host import host

from bes.config.simple_config_editor import simple_config_editor
from bes.config.simple_config_options import simple_config_options
from bes.python.python_version import python_version

from .python_error import python_error

class python_exe_config(object):
  '''
  Class to manage python executables by system and version.  For example:

macos
  2.7: /usr/bin/python2.7
  3.7: /usr/local/opt/python@3.7/bin/python3.7
  3.8: /usr/local/opt/python@3.8/bin/python3.8
  3.9: /usr/local/opt/python@3.9/bin/python3.9

windows
  2.7: C:/Python27/python.exe
  3.7: C:/Program Files/Python37/python.exe
  3.8: C:/Program Files/Python38/python.exe
  3.9: C:/Program Files/Python39/python.exe
  '''

  _log = logger('pip')
  
  def __init__(self, filename):
    check.check_string(filename)

    options = simple_config_options(key_check_type = simple_config_options.KEY_CHECK_ANY)
    self._config = simple_config_editor(filename, options = options)

  def get_python_exe(self, version, system = None, distro = None):
    python_version.check_version(version)
    check.check_string(system, allow_none = True)
    check.check_string(distro, allow_none = True)

    section_name = self._make_section_name(system, distro)
    return self._config.get_value_with_default(section_name, version, None)

  def set_python_exe(self, version, exe, system = None, distro = None):
    python_version.check_version(version)
    check.check_string(system, allow_none = True)
    check.check_string(distro, allow_none = True)

    section_name = self._make_section_name(system, distro)
    return self._config.set_value(section_name, version, exe)
  
  @classmethod
  def _make_section_name(clazz, system, distro):
    check.check_string(system, allow_none = True)
    check.check_string(distro, allow_none = True)
    
    if system:
      host.check_system(system)
    else:
      system = host.SYSTEM

    if distro:
      host.check_distro(system, distro)
    elif distro == None:
      distro = host.DISTRO
    else:
      distro = ''
      
    if system in ( host.WINDOWS, host.MACOS ):
      section_name = system
    elif system in ( host.LINUX ):
      if distro:
        section_name = '{}.{}'.format(system, distro)
      else:
        section_name = system
    else:
      host.raise_unsupported_system(system = system)
    return section_name
