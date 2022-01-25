#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from bes.cli.cli_options import cli_options
from bes.common.check import check
from bes.script.blurber import blurber

from .files_cli_options import files_cli_options

class file_split_options(files_cli_options):

  def __init__(self, **kargs):
    super(file_split_options, self).__init__(**kargs)

  @classmethod
  #@abstractmethod
  def default_values(clazz):
    'Return a dict of defaults for these options.'
    return clazz.super_default_values({
      'blurber': blurber(),
      'check_downloading': True,
      'check_downloading_extension': 'part',
      'check_modified': False,
      'check_modified_interval': 250.0,
    })
  
  @classmethod
  #@abstractmethod
  def value_type_hints(clazz):
    return clazz.super_value_type_hints({
      'check_downloading': bool,
      'check_modified': bool,
      'check_modified_interval': float,
    })

  #@abstractmethod
  def check_value_types(self):
    'Check the type of each option.'
    super(file_split_options, self).check_value_types()
    check.check_bool(self.check_downloading)
    check.check_string(self.check_downloading_extension)
    check.check_bool(self.check_modified)
    check.check_float(self.check_modified_interval)
    check.check_blurber(self.blurber)

check.register_class(file_split_options)
