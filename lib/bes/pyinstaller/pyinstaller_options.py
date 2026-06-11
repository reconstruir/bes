#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.bcli.bcli_options import bcli_options
from bes.bcli.bcli_options_desc import bcli_options_desc

from .pyinstaller_error import pyinstaller_error
from .pyinstaller_log_level import cli_pyinstaller_log_level_type

class _pyinstaller_options_desc(bcli_options_desc):

  def _options_desc(self):
    return '''
          build_dir  str       default=${_build_dir}
              clean  bool      default=True
    config_filename  str       default=None
              debug  bool      default=False
           excludes  list[str] default=None
    hidden_imports   list[str] default=None
          log_level  pyinstaller_log_level  default=${_log_level}
osx_bundle_identifier str      default=None
     python_version  str       default=3.8
        replace_env  dict      default=None
            verbose  bool      default=False
           windowed  bool      default=False
'''

  def _types(self):
    return [ cli_pyinstaller_log_level_type ]

  def _error_class(self):
    return pyinstaller_error

  def _variables(self):
    from .pyinstaller_defaults import pyinstaller_defaults
    return {
      '_build_dir': lambda: pyinstaller_defaults.BUILD_DIR,
      '_log_level': lambda: pyinstaller_defaults.LOG_LEVEL,
    }

class pyinstaller_options(bcli_options):
  def __init__(self, **kwargs):
    super().__init__(_pyinstaller_options_desc(), **kwargs)

pyinstaller_options.register_check_class()
