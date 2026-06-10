#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.bcli.bcli_options import bcli_options
from bes.bcli.bcli_options_desc import bcli_options_desc

from .native_package_error import native_package_error

class _native_package_command_options_desc(bcli_options_desc):

  def _options_desc(self):
    return '''
verbose       bool  default=False
debug         bool  default=False
sudo_password str   secret=True
'''

  def _error_class(self):
    return native_package_error

class native_package_command_options(bcli_options):
  def __init__(self, **kwargs):
    super().__init__(_native_package_command_options_desc(), **kwargs)

native_package_command_options.register_check_class()
