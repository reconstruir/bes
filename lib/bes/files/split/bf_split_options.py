#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from datetime import datetime
from os import path

from bes.cli.cli_options import cli_options
from bes.system.check import check
from bes.script.blurber import blurber

from bes.fs.files_cli_options import files_cli_options

class bf_split_options_desc(bcli_options_desc):

  def __init__(self, **kargs):

class bf_split_options_desc(bcli_options_desc):

  def __init__(self, **kargs):
    


class bf_split_options(files_cli_options):

  def __init__(self, **kargs):
    super().__init__(**kargs)


register_default('default_dup_file_timestamp', lambda : time_util.timestamp())
register_default('default_timestamp', lambda : datetime.now())

'''
debug              bool       False
dry_run            bool       False
quiet              bool       False
recursive          bool       False
verbose            bool       False
ignore_files       list[str]  None
dup_file_timestamp str        default_dup_file_timestamp
dup_file_count     int        1
'''

'''
check_downloading           bool       false
check_downloading_extension str        part
check_modified              bool       false
check_modified_interval     float      250.0
existing_file_timestamp     datetime   now
ignore_extensions           list[str]  None
unzip                       bool       false
ignore_incomplete           bool       false
'''

class bf_split_options(files_cli_options):

  def __init__(self, **kargs):
    super().__init__(**kargs)

  @classmethod
  #@abstractmethod
  def default_values(clazz):
    'Return a dict of defaults for these options.'
    return clazz.super_default_values({
      'blurber': blurber(),
      'check_downloading': False,
      'check_downloading_extension': 'part',
      'check_modified': False,
      'check_modified_interval': 250.0,
      'existing_file_timestamp': datetime.now(),
      'ignore_extensions': None,
      'unzip': False,
      'ignore_incomplete': False,
    })
  
  @classmethod
  #@abstractmethod
  def value_type_hints(clazz):
    return clazz.super_value_type_hints({
      'check_downloading': bool,
      'check_modified': bool,
      'check_modified_interval': float,
      'unzip': bool,
#      'ignore_extensions': set,
#      'existing_file_timestamp': datetime,
      'ignore_incomplete': bool,
    })

  #@abstractmethod
  def check_value_types(self):
    'Check the type of each option.'
    super().check_value_types()
    check.check_bool(self.check_downloading)
    check.check_string(self.check_downloading_extension)
    check.check_bool(self.check_modified)
    check.check_float(self.check_modified_interval)
    check.check_blurber(self.blurber)
    check.check(self.existing_file_timestamp, datetime, allow_none = True)
    check.check_string_seq(self.ignore_extensions, allow_none = True)
    check.check_bool(self.unzip)
    check.check_bool(self.ignore_incomplete)

check.register_class(bf_split_options)
