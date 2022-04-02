#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.cli.cli_options import cli_options
from bes.common.check import check
from bes.common.time_util import time_util

from .dir_partition_criteria_base import dir_partition_criteria_base
from .dir_partition_defaults import dir_partition_defaults
from .dir_partition_type import dir_partition_type
from .files_cli_options import files_cli_options

class dir_partition_options(files_cli_options):

  def __init__(self, **kargs):
    super(dir_partition_options, self).__init__(**kargs)

  @classmethod
  #@abstractmethod
  def default_values(clazz):
    'Return a dict of defaults for these options.'
    return clazz.super_default_values({
      'dup_file_timestamp': time_util.timestamp(),
      'dup_file_count': 1,
      'partition_type': dir_partition_defaults.PARTITION_TYPE,
      'partition_criteria': None,
      'flat': False,
      'threshold': dir_partition_defaults.THRESHOLD,
      'dst_dir': dir_partition_defaults.DST_DIR,
      'delete_empty_dirs': dir_partition_defaults.DELETE_EMPTY_DIRS,
    })
  
  @classmethod
  #@abstractmethod
  def value_type_hints(clazz):
    return clazz.super_value_type_hints({
      'dup_file_count': int,
      'partition_type': dir_partition_type,
#      'partition_criteria': dir_partition_criteria_base,
      'flat': bool,
      'threshold': int,
      'delete_empty_dirs': bool,
    })

  #@abstractmethod
  def check_value_types(self):
    'Check the type of each option.'
    super(dir_partition_options, self).check_value_types()
    check.check_string(self.dup_file_timestamp)
    check.check_int(self.dup_file_count)
    check.check_dir_partition_type(self.partition_type, allow_none = True)
    check.check_dir_partition_criteria(self.partition_criteria, allow_none = True)
    check.check_bool(self.flat)
    check.check_int(self.threshold)
    check.check_string(self.dst_dir)
    check.check_bool(self.delete_empty_dirs)

check.register_class(dir_partition_options)
