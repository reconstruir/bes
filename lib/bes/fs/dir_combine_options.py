#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.cli.cli_options import cli_options
from bes.common.check import check
from bes.common.time_util import time_util

from .files_cli_options import files_cli_options

class dir_combine_options(files_cli_options):

  def __init__(self, **kargs):
    super(dir_combine_options, self).__init__(**kargs)

  @classmethod
  #@abstractmethod
  def default_values(clazz):
    'Return a dict of defaults for these options.'
    return clazz.super_default_values({
      'dup_file_timestamp': time_util.timestamp(),
      'dup_file_count': 1,
      'destination_dir': None,
    })
  
  @classmethod
  #@abstractmethod
  def value_type_hints(clazz):
    return clazz.super_value_type_hints({
      'dup_file_count': int,
    })

  #@abstractmethod
  def check_value_types(self):
    'Check the type of each option.'
    super(dir_combine_options, self).check_value_types()
    check.check_string(self.dup_file_timestamp)
    check.check_int(self.dup_file_count)
    check.check_string(self.destination_dir, allow_none = True)


check.register_class(dir_combine_options)
