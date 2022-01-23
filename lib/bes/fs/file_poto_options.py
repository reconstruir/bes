#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.cli.cli_options import cli_options
from bes.common.check import check
from bes.common.time_util import time_util

from .files_cli_options import files_cli_options
from .file_poto_type import file_poto_type

class file_poto_options(files_cli_options):

  def __init__(self, **kargs):
    super(file_poto_options, self).__init__(**kargs)

  @classmethod
  #@abstractmethod
  def default_values(clazz):
    'Return a dict of defaults for these options.'
    return clazz.super_default_values({
      'dup_file_timestamp': time_util.timestamp(),
      'dup_file_count': 1,
      'partition_type': None,
      'flat': False,
      'threshold': 2,
    })
  
  @classmethod
  #@abstractmethod
  def value_type_hints(clazz):
    return clazz.super_value_type_hints({
      'dup_file_count': int,
      'partition_type': file_poto_type,
      'flat': bool,
      'threshold': int,
    })

  #@abstractmethod
  def check_value_types(self):
    'Check the type of each option.'
    super(file_poto_options, self).check_value_types()
    check.check_string(self.dup_file_timestamp)
    check.check_int(self.dup_file_count)
    check.check_file_poto_type(self.partition_type, allow_none = True)
    check.check_bool(self.flat)
    check.check_int(self.threshold)

check.register_class(file_poto_options)
