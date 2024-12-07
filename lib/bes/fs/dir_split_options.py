#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.bcli.bcli_options import bcli_options
from bes.bcli.bcli_options_desc import bcli_options_desc

from .files_cli_options import files_cli_options
from .files_cli_options import _files_cli_options_desc

from bes.cli.cli_options import cli_options
from ..system.check import check
from bes.common.time_util import time_util

from .dir_split_defaults import dir_split_defaults
from .file_sort_order import file_sort_order
from .file_sort_order import cli_file_sort_order_type
from .files_cli_options import files_cli_options

class _dir_split_options_desc(_files_cli_options_desc):

  #@abstractmethod
  def _types(self):
    return [
      cli_file_sort_order_type,
    ]
  
  #@abstractmethod
  def _options_desc(self):
    return self.combine_options_desc(super()._options_desc(), f'''
  chunk_size int             default={dir_split_defaults.CHUNK_SIZE}
      prefix str             default={dir_split_defaults.PREFIX}
  sort_order file_sort_order default={dir_split_defaults.SORT_ORDER}
sort_reverse bool            default={dir_split_defaults.SORT_REVERSE}
   threshold int             default={dir_split_defaults.THRESHOLD}
''')
  
class dir_split_options(bcli_options):
  def __init__(self, **kwargs):
    super().__init__(_dir_split_options_desc(), **kwargs)

dir_split_options.register_check_class()
