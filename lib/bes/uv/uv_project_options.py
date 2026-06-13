#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os
from os import path

from bes.bcli.bcli_options import bcli_options
from bes.bcli.bcli_options_desc import bcli_options_desc

from . import uv_error
from . import uv_exe

class _uv_project_options_desc(bcli_options_desc):

  def _options_desc(self):
    return '''
uv_exe       str  default=None
python       str  default=None
root_dir     str  default=None
uv_cache_dir str  default=None
verbose      bool default=False
debug        bool default=False
'''

  def _error_class(self):
    return uv_error.uv_error

class uv_project_options(bcli_options):

  def __init__(self, **kwargs):
    super().__init__(_uv_project_options_desc(), **kwargs)

  def resolve_root_dir(self):
    if self.root_dir:
      return path.abspath(self.root_dir)
    return path.join(os.getcwd(), 'UV_PROJECT_ROOT')

  def resolve_uv_exe(self):
    return uv_exe.uv_exe.find(self.uv_exe)

uv_project_options.register_check_class()
