#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.bcli.bcli_options import bcli_options
from bes.bcli.bcli_options_desc import bcli_options_desc

from . import uv_error

class _uv_project_command_options_desc(bcli_options_desc):

  def _options_desc(self):
    return '''
verbose  bool default=False
debug    bool default=False
uv_exe   str  default=None
python   str  default=None
root_dir str  default=None
'''

  def _error_class(self):
    return uv_error.uv_error

class uv_project_command_options(bcli_options):

  def __init__(self, **kwargs):
    super().__init__(_uv_project_command_options_desc(), **kwargs)

uv_project_command_options.register_check_class()
