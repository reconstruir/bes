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
  def name(self):
    return '_dir_split_options_desc'

  #@abstractmethod
  def types(self):
    return [
      cli_file_sort_order_type(),
    ]
  
  #@abstractmethod
  def options_desc(self):
    return self.combine_options_desc(super().options_desc(), f'''
        chunk_size int                      default={dir_split_defaults.CHUNK_SIZE}
        prefix     str                      default={dir_split_defaults.PREFIX}
        sort_order cli_file_sort_order_type default={dir_split_defaults.SORT_ORDER}
      sort_reverse bool                     default={dir_split_defaults.SORT_REVERSE}
         threshold int                      default={dir_split_defaults.THRESHOLD}
''')
  
  #@abstractmethod
  def variables(self):
    return self.combine_variables(super().variables(), {
      '_timestamp': lambda: time_util.timestamp(),
    })

class dir_split_options(bcli_options):
  def __init__(self, **kwargs):
    super().__init__(_dir_split_options_desc(), **kwargs)

dir_split_options.register_check_class()

class xxxdir_split_options(files_cli_options):

  def __init__(self, **kargs):
    super(dir_split_options, self).__init__(**kargs)

  @classmethod
  #@abstractmethod
  def default_values(clazz):
    'Return a dict of defaults for these options.'
    return clazz.super_default_values({
      'chunk_size': dir_split_defaults.CHUNK_SIZE,
      'prefix': dir_split_defaults.PREFIX,
      'dup_file_timestamp': time_util.timestamp(),
      'dup_file_count': 1,
      'sort_order': dir_split_defaults.SORT_ORDER,
      'sort_reverse': dir_split_defaults.SORT_REVERSE,
      'threshold': dir_split_defaults.THRESHOLD,
    })
  
  @classmethod
  #@abstractmethod
  def value_type_hints(clazz):
    return clazz.super_value_type_hints({
      'chunk_size': int,
      'dup_file_count': int,
      'sort_order': file_sort_order,
      'sort_reverse': bool,
      'threshold': int,
    })

  #@abstractmethod
  def check_value_types(self):
    'Check the type of each option.'
    super(dir_split_options, self).check_value_types()
    check.check_int(self.chunk_size)
    check.check_string(self.prefix)
    check.check_string(self.dup_file_timestamp)
    check.check_int(self.dup_file_count)
    check.check_file_sort_order(self.sort_order, allow_none = True)
    check.check_bool(self.sort_reverse)
    check.check_int(self.threshold, allow_none = True)

#check.register_class(dir_split_options)
