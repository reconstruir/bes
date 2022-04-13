#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from ..cli.cli_options import cli_options
from ..system.check import check

from .files_cli_options import files_cli_options
from .dir_combine_defaults import dir_combine_defaults

class dir_combine_options(files_cli_options):

  def __init__(self, **kargs):
    super(dir_combine_options, self).__init__(**kargs)

  @classmethod
  #@abstractmethod
  def default_values(clazz):
    'Return a dict of defaults for these options.'
    return clazz.super_default_values({
      'dup_file_timestamp': dir_combine_defaults.DUP_FILE_TIMESTAMP,
      'dup_file_count': dir_combine_defaults.DUP_FILE_COUNT,
      'destination_dir': None,
      'ignore_empty': dir_combine_defaults.IGNORE_EMPTY,
      'flatten': dir_combine_defaults.FLATTEN,
      'delete_empty_dirs': dir_combine_defaults.DELETE_EMPTY_DIRS,
    })
  
  @classmethod
  #@abstractmethod
  def value_type_hints(clazz):
    return clazz.super_value_type_hints({
      'dup_file_count': int,
      'ignore_empty': bool,
      'flatten': bool,
      'delete_empty_dirs': bool,
    })

  #@abstractmethod
  def check_value_types(self):
    'Check the type of each option.'
    super(dir_combine_options, self).check_value_types()
    check.check_string(self.dup_file_timestamp)
    check.check_int(self.dup_file_count)
    check.check_string(self.destination_dir, allow_none = True)
    check.check_bool(self.ignore_empty)
    check.check_bool(self.flatten)
    check.check_bool(self.delete_empty_dirs)

check.register_class(dir_combine_options)
