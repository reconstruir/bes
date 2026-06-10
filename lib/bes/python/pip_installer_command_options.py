#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.bcli.bcli_options import bcli_options
from bes.bcli.bcli_options_desc import bcli_options_desc

from .pip_error import pip_error

class _pip_installer_command_options_desc(bcli_options_desc):

  def _options_desc(self):
    return '''
verbose    bool  default=False
debug      bool  default=False
root_dir   str
python_exe str
'''

  def _error_class(self):
    return pip_error

class pip_installer_command_options(bcli_options):
  def __init__(self, **kwargs):
    super().__init__(_pip_installer_command_options_desc(), **kwargs)

pip_installer_command_options.register_check_class()
