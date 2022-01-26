#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.cli.cli_options import cli_options
from bes.common.check import check
from bes.common.time_util import time_util

from .dir_split_conflict_strategy import dir_split_conflict_strategy
from .file_sort_order import file_sort_order
from .files_cli_options import files_cli_options

class dir_split_options(files_cli_options):

  def __init__(self, **kargs):
    super(dir_split_options, self).__init__(**kargs)

  @classmethod
  #@abstractmethod
  def default_values(clazz):
    'Return a dict of defaults for these options.'
    return clazz.super_default_values({
      'chunk_size': 250,
      'prefix': 'split-',
      'dup_file_timestamp': time_util.timestamp(),
      'dup_file_count': 1,
      'sort_order': file_sort_order.FILENAME,
      'sort_reverse': False,
      'conflict_strategy': None,
    })
  
  @classmethod
  #@abstractmethod
  def value_type_hints(clazz):
    return clazz.super_value_type_hints({
      'chunk_size': int,
      'dup_file_count': int,
      'sort_order': file_sort_order,
      'sort_reverse': bool,
      'conflict_strategy': dir_split_conflict_strategy,
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
    check.check_dir_split_conflict_strategy(self.conflict_strategy, allow_none = True)

check.register_class(dir_split_options)
