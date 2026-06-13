#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.bcli.bcli_options import bcli_options
from bes.bcli.bcli_options_desc import bcli_options_desc

from .bes_project_error import bes_project_error

class _bes_project_command_options_desc(bcli_options_desc):

  def _options_desc(self):
    return '''
verbose         bool  default=False
debug           bool  default=False
name            str   default=None
root_dir        str
output_filename str
output_style    str   default=table
uv_exe          str   default=None
'''

  def _error_class(self):
    return bes_project_error

class bes_project_command_options(bcli_options):
  def __init__(self, **kwargs):
    super().__init__(_bes_project_command_options_desc(), **kwargs)

bes_project_command_options.register_check_class()
