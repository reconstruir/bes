#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.bcli.bcli_options import bcli_options
from bes.bcli.bcli_options_desc import bcli_options_desc

from ..cli.cli_options import cli_options
from ..system.check import check

from .files_cli_options import files_cli_options
from .files_cli_options import _files_cli_options_desc
from .dir_combine_defaults import dir_combine_defaults

class _dir_combine_options_desc(_files_cli_options_desc):

  #@abstractmethod
  def _options_desc(self):
    return self.combine_options_desc(super()._options_desc(), f'''
  destination_dir str
     ignore_empty bool default={dir_combine_defaults.IGNORE_EMPTY}
          flatten bool default={dir_combine_defaults.FLATTEN},
delete_empty_dirs bool default={dir_combine_defaults.DELETE_EMPTY_DIRS}
''')
  
class dir_combine_options(bcli_options):
  def __init__(self, **kwargs):
    super().__init__(_dir_combine_options_desc(), **kwargs)

  def pass_through_keys(self):
    return tuple(list(super().pass_through_keys()) + [ 'files', ])
    
dir_combine_options.register_check_class()
