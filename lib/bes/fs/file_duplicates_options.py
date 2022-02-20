#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from bes.cli.cli_options import cli_options
from bes.common.check import check
from bes.common.time_util import time_util
from bes.fs.file_ignore_item import file_ignore_item
from bes.fs.file_multi_ignore import file_multi_ignore
from bes.property.cached_property import cached_property
from bes.script.blurber import blurber

from .files_cli_options import files_cli_options
from .file_util import file_util

class file_duplicates_options(files_cli_options):

  def __init__(self, **kargs):
    super(file_duplicates_options, self).__init__(**kargs)

  @classmethod
  #@abstractmethod
  def default_values(clazz):
    'Return a dict of defaults for these options.'
    return clazz.super_default_values({
      'blurber': blurber(),
      'small_checksum_size': 1024 * 1024,
      'prefer_prefixes': None,
      'sort_key': None,
      'include_empty_files': False,
      'ignore_files': [],
    })
  
  @classmethod
  #@abstractmethod
  def value_type_hints(clazz):
    return clazz.super_value_type_hints({
      'small_checksum_size': int,
      'prefer_prefixes': list,
      'include_empty_files': bool,
      'ignore_files': list,
      #'sort_key': callable,
    })

  #@abstractmethod
  def check_value_types(self):
    'Check the type of each option.'
    super(file_duplicates_options, self).check_value_types()
    check.check_int(self.small_checksum_size)
    check.check_string_seq(self.prefer_prefixes, allow_none = True)
    check.check_function(self.sort_key, allow_none = True)
    check.check_bool(self.include_empty_files)
    check.check_blurber(self.blurber)
    check.check_string_seq(self.ignore_files)

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

  @cached_property
  def file_ignorer(self):
    return file_multi_ignore(self.ignore_files)

  def should_ignore_file(self, filename):
    return self.file_ignorer.should_ignore(filename)
  
check.register_class(file_duplicates_options)