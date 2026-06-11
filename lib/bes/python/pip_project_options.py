#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.bcli.bcli_options import bcli_options
from bes.bcli.bcli_options_desc import bcli_options_desc
from bes.data_output.data_output_options_mixin import data_output_options_mixin

from .pip_error import pip_error

class _pip_project_options_desc(bcli_options_desc):
  def _options_desc(self):
    return '''
  debug            bool  default=False
  output_filename  str   default=None
  output_style     str   default=table
  python_exe       str   default=None
  python_version   str   default=None
  root_dir         str   default=None
  verbose          bool  default=False
  limit_num_items  int   default=None
'''
  def _error_class(self): return pip_error

class pip_project_options(bcli_options, data_output_options_mixin):
  def __init__(self, **kwargs):
    super().__init__(_pip_project_options_desc(), **kwargs)

  def resolve_python_exe(self):
    if self.python_exe:
      return self.python_exe

    from .python_exe import python_exe
    if not self.python_version:
      exe = python_exe.default_exe()
      if not exe:
        raise pip_error('No default python found')
    else:
      exe = python_exe.find_version(self.python_version)
      if not exe:
        raise pip_error('No python found for version "{}"'.format(self.python_version))
    return exe

  def resolve_root_dir(self):
    import os.path as path
    if self.root_dir:
      return path.abspath(self.root_dir)
    import os
    return path.join(os.getcwd(), 'BES_PIP_ROOT')

pip_project_options.register_check_class()
