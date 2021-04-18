#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from bes.common.check import check
from bes.system.log import logger

from bes.config.simple_config_editor import simple_config_editor
from bes.config.simple_config_options import simple_config_options

from .pip_error import pip_error
from .pip_exe import pip_exe

class pip_project_config(object):
  'Class to manager a pip project config.'

  _log = logger('pip')
  
  def __init__(self, filename):
    check.check_string(filename)

    options = simple_config_options(key_check_type = simple_config_options.KEY_CHECK_ANY)
    self._config = simple_config_editor(filename, options = options)

  @property
  def python_exe(self):
    return self._config.get_value_with_default('pip_project', 'python_exe', None)

  @property
  def python_exe(self):
    return self._config.get_value_with_default('pip_project', 'python_exe', None)

  @python_exe.setter
  def python_exe(self, python_exe):
    return self._config.set_value('pip_project', 'python_exe', python_exe)
