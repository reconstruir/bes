#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.bcli.bcli_options import bcli_options
from bes.bcli.bcli_options_desc import bcli_options_desc

from bes.cli.cli_options import cli_options
from ..system.check import check
from bes.common.time_util import time_util

from .dir_partition_criteria_base import cli_dir_partition_criteria
from .dir_partition_defaults import dir_partition_defaults
from .dir_partition_type import dir_partition_type
from .dir_partition_type import cli_dir_partition_type
from .files_cli_options import files_cli_options
from .files_cli_options import _files_cli_options_desc

class _dir_partition_options_desc(_files_cli_options_desc):

  #@abstractmethod
  def _types(self):
    return [
      cli_dir_partition_type,
      cli_dir_partition_criteria,
    ]
  
  #@abstractmethod
  def _options_desc(self):
    return self.combine_options_desc(super()._options_desc(), f'''
    partition_type dir_partition_type default={dir_partition_defaults.PARTITION_TYPE}
partition_criteria dir_partition_criteria
           flatten bool default={dir_partition_defaults.FLATTEN},
         threshold int  default={dir_partition_defaults.THRESHOLD}
           dst_dir str  default={dir_partition_defaults.DST_DIR},
 delete_empty_dirs bool default={dir_partition_defaults.DELETE_EMPTY_DIRS}
''')
  
class dir_partition_options(bcli_options):
  def __init__(self, **kwargs):
    super().__init__(_dir_partition_options_desc(), **kwargs)

  def pass_through_keys(self):
    return tuple(list(super().pass_through_keys()) + [ 'files', ])
    
dir_partition_options.register_check_class()
