#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.bcli.bcli_options import bcli_options
from bes.bcli.bcli_options_desc import bcli_options_desc

from .pyinstaller_error import pyinstaller_error

class _pyinstaller_command_options_desc(bcli_options_desc):

  def _options_desc(self):
    return '''
verbose  bool  default=False
debug    bool  default=False
'''

  def _error_class(self):
    return pyinstaller_error

class pyinstaller_command_options(bcli_options):
  def __init__(self, **kwargs):
    super().__init__(_pyinstaller_command_options_desc(), **kwargs)

pyinstaller_command_options.register_check_class()
