#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os
from os import path

from bes.bcli.bcli_options import bcli_options
from bes.bcli.bcli_options_desc import bcli_options_desc
from bes.data_output.data_output_options import data_output_options
from bes.property.cached_property import cached_property

from .bat_project_error import bat_project_error

class _bat_project_options_desc(bcli_options_desc):
  def _options_desc(self):
    return '''
  debug            bool  default=False
  name             str   default=None
  output_filename  str   default=None
  output_style     str   default=table
  root_dir         str   default=None
  uv_exe           str   default=None
  verbose          bool  default=False
'''
  def _error_class(self): return bat_project_error

class bat_project_options(bcli_options):
  def __init__(self, **kwargs):
    super().__init__(_bat_project_options_desc(), **kwargs)

  def resolve_root_dir(self):
    if self.root_dir:
      return path.abspath(self.root_dir)
    return path.join(os.getcwd(), 'BES_PROJECT_ROOT')

  @cached_property
  def data_output_options(self):
    return data_output_options(output_filename = self.output_filename,
                               style = self.output_style)

  def pass_through_keys(self):
    return ('data_output_options',)

bat_project_options.register_check_class()
