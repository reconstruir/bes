#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from bes.bcli.bcli_options import bcli_options
from bes.bcli.bcli_options_desc import bcli_options_desc

from bes.cli.cli_options import cli_options
from ..system.check import check
from bes.common.time_util import time_util
from bes.script.blurber import blurber

from bes.fs.file_ignore_options_mixin import file_ignore_options_mixin

from .file_duplicates_setup import file_duplicates_setup
from .file_duplicates_setup import cli_file_duplicates_setup
from .file_util import file_util
from .files_cli_options import files_cli_options
from .files_cli_options import _files_cli_options_desc
from .file_duplicates_defaults import file_duplicates_defaults

'''
class file_duplicates_options(files_cli_options, file_ignore_options_mixin):

  def __init__(self, **kargs):
    super().__init__(**kargs)

  @classmethod
  #@abstractmethod
  def default_values(clazz):
    'Return a dict of defaults for these options.'
    return clazz.super_default_values({
      'blurber': blurber(),
      'small_checksum_size': file_duplicates_defaults.SMALL_CHECKSUM_SIZE,
      'prefer_prefixes': None,
      'sort_key': None,
      'include_empty_files': file_duplicates_defaults.INCLUDE_EMPTY_FILES,
      'ignore_files': None,
      'preparation': None,
      'delete_empty_dirs': file_duplicates_defaults.DELETE_EMPTY_DIRS,
    })
  
  @classmethod
  #@abstractmethod
  def value_type_hints(clazz):
    return clazz.super_value_type_hints({
      'small_checksum_size': int,
      'prefer_prefixes': list,
      'include_empty_files': bool,
      'ignore_files': list,
      'preparation': file_duplicates_setup,
      #'sort_key': callable,
      'delete_empty_dirs': bool,
    })

  #@abstractmethod
  def check_value_types(self):
    'Check the type of each option.'
    super(file_duplicates_options, self).check_value_types()
    check.check_int(self.small_checksum_size)
    check.check_string_seq(self.prefer_prefixes, allow_none = True)
    check.check_callable(self.sort_key, allow_none = True)
    check.check_bool(self.include_empty_files)
    check.check_blurber(self.blurber)
    check.check_string_seq(self.ignore_files, allow_none = True)
    check.check_file_duplicates_setup(self.preparation, allow_none = True)
    check.check_bool(self.delete_empty_dirs)

  @staticmethod
  def sort_key_modification_date(filename):
    return ( file_util.get_modification_date(filename), )

  @staticmethod
  def sort_key_basename_length(filename):
    return ( len(path.basename(filename)),  )

  @staticmethod
  def sort_key(filename):
    mtime = file_duplicates_options.sort_key_modification_date(filename)
    length = file_duplicates_options.sort_key_basename_length(filename)
    return ( mtime, length )
  
check.register_class(file_duplicates_options)
'''

# FUCK

class _file_duplicates_options_desc(_files_cli_options_desc):

  #@abstractmethod
  def types(self):
    return [
      cli_file_duplicates_setup(),
    ]
  
  #@abstractmethod
  def name(self):
    return '_file_duplicates_options_desc'
  
  #@abstractmethod
  def options_desc(self):
    return self.combine_options_desc(super().options_desc(), f'''
      small_checksum_size int default={file_duplicates_defaults.SMALL_CHECKSUM_SIZE}
      prefer_prefixes list[str]
      sort_key callable
      include_empty_files bool default={file_duplicates_defaults.INCLUDE_EMPTY_FILES}
      preparation file_duplicates_setup
      delete_empty_dirs bool default={file_duplicates_defaults.DELETE_EMPTY_DIRS}
''')
  
class file_duplicates_options(bcli_options, file_ignore_options_mixin):
  def __init__(self, **kwargs):
    super().__init__(_file_duplicates_options_desc(), **kwargs)

#  def pass_through_keys(self):
#    return tuple(list(super().pass_through_keys()) + [ 'files', ])

  @staticmethod
  def sort_key_modification_date(filename):
    return ( file_util.get_modification_date(filename), )

  @staticmethod
  def sort_key_basename_length(filename):
    return ( len(path.basename(filename)),  )

  @staticmethod
  def sort_key(filename):
    mtime = file_duplicates_options.sort_key_modification_date(filename)
    length = file_duplicates_options.sort_key_basename_length(filename)
    return ( mtime, length )

file_duplicates_options.register_check_class()
