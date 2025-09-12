#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from bes.bcli.bcli_options import bcli_options
from bes.bcli.bcli_options_desc import bcli_options_desc

from bes.cli.cli_options import cli_options
from bes.system.check import check
from bes.common.time_util import time_util
from bes.script.blurber import blurber

from bes.fs.files_cli_options import files_cli_options
from bes.fs.files_cli_options import _files_cli_options_desc

from ..bf_file_type import bf_cli_file_type

from ..ignore.bf_file_ignore_options_mixin import bf_file_ignore_options_mixin

from .bf_file_duplicates_setup import bf_file_duplicates_setup
from .bf_file_duplicates_setup import cli_bf_file_duplicates_setup

class _bf_file_duplicates_options_desc(_files_cli_options_desc):

  #@abstractmethod
  def _types(self):
    
    return [
      cli_bf_file_duplicates_setup,
      bf_cli_file_type,
    ]
  
  #@abstractmethod
  def _options_desc(self):
    return self.combine_options_desc(super()._options_desc(), f'''
          file_type bf_file_type            default=FILE_OR_LINK
                 max_depth int
                 min_depth int
    prefer_prefixes list[str]
           sort_key callable               default=${{_default_sort_key}}
include_empty_files bool                   default=False
        preparation bf_file_duplicates_setup
  delete_empty_dirs bool                   default=False
 include_hard_links bool                   default=False
 include_soft_links bool                   default=False
''')

  #@abstractmethod
  def _variables(self):
    return self.combine_variables(super()._variables(), {
      '_default_sort_key': lambda: bf_file_duplicates_options.mtime_sort_key,
    })
  
class bf_file_duplicates_options(bcli_options, bf_file_ignore_options_mixin):
  def __init__(self, **kwargs):
    super().__init__(_bf_file_duplicates_options_desc(), **kwargs)

  @staticmethod
  def sort_key_modification_date(filename):
    return ( file_util.get_modification_date(filename), )

  @staticmethod
  def sort_key_basename_length(filename):
    return ( len(path.basename(filename)),  )

  @staticmethod
  def mtime_sort_key(filename):
    mtime = bf_file_duplicates_options.sort_key_modification_date(filename)
    length = bf_file_duplicates_options.sort_key_basename_length(filename)
    return ( mtime, length )

bf_file_duplicates_options.register_check_class()
