#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from bes.bcli.bcli_options import bcli_options
from bes.bcli.bcli_options_desc import bcli_options_desc

from bes.cli.cli_options import cli_options
from ..system.check import check
from bes.common.time_util import time_util
from bes.script.blurber import blurber

from bes.fs.file_ignore_options_mixin import file_ignore_options_mixin

from .bf_file_duplicates_setup import bf_file_duplicates_setup
from .bf_file_duplicates_setup import cli_bf_file_duplicates_setup
from .file_util import file_util
from .files_cli_options import files_cli_options
from .files_cli_options import _files_cli_options_desc
from .bf_file_duplicates_defaults import bf_file_duplicates_defaults

class _file_duplicates_options_desc(_files_cli_options_desc):

  #@abstractmethod
  def _types(self):
    
    return [
      cli_bf_file_duplicates_setup,
    ]
  
  #@abstractmethod
  def _options_desc(self):
    return self.combine_options_desc(super()._options_desc(), f'''
    prefer_prefixes list[str]
           sort_key callable               default=${{_default_sort_key}}
include_empty_files bool                   default={bf_file_duplicates_defaults.INCLUDE_EMPTY_FILES}
        preparation bf_file_duplicates_setup
  delete_empty_dirs bool                   default={bf_file_duplicates_defaults.DELETE_EMPTY_DIRS}
 include_hard_links bool                   default={bf_file_duplicates_defaults.INCLUDE_HARD_LINKS}
 include_soft_links bool                   default={bf_file_duplicates_defaults.INCLUDE_SOFT_LINKS}
''')

  #@abstractmethod
  def _variables(self):
    return self.combine_variables(super()._variables(), {
      '_default_sort_key': lambda: file_duplicates_options.mtime_sort_key,
    })
  
class file_duplicates_options(bcli_options, file_ignore_options_mixin):
  def __init__(self, **kwargs):
    super().__init__(_file_duplicates_options_desc(), **kwargs)

  @staticmethod
  def sort_key_modification_date(filename):
    return ( file_util.get_modification_date(filename), )

  @staticmethod
  def sort_key_basename_length(filename):
    return ( len(path.basename(filename)),  )

  @staticmethod
  def mtime_sort_key(filename):
    mtime = file_duplicates_options.sort_key_modification_date(filename)
    length = file_duplicates_options.sort_key_basename_length(filename)
    return ( mtime, length )

file_duplicates_options.register_check_class()
