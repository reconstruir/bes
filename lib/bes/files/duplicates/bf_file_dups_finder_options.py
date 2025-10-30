#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from bes.bcli.bcli_options import bcli_options
from bes.bcli.bcli_options_desc import bcli_options_desc

from bes.cli.cli_options import cli_options
from bes.system.check import check
from bes.common.time_util import time_util
from bes.script.blurber import blurber

from ..core.bf_files_cli_options import bf_files_cli_options
from ..core.bf_files_cli_options import _bf_files_cli_options_desc

from ..resolve.bf_file_resolver_options import bf_file_resolver_options

from ..bf_file_type import bf_cli_file_type

from .bf_file_dups_entry_list import bf_file_dups_entry_list

#from .bf_file_dups_finder_setup import bf_file_dups_finder_setup
#from .bf_file_dups_finder_setup import cli_bf_file_dups_finder_setup

class _bf_file_dups_finder_options_desc(_bf_files_cli_options_desc):

  #@abstractmethod
  def _types(self):
    
    return [
#      cli_bf_file_dups_finder_setup,
      bf_cli_file_type,
    ]
  
  #@abstractmethod
  def _options_desc(self):
    return '''
          file_type    bf_file_type  default=FILE_OR_LINK
          max_depth    int
          min_depth    int
    prefer_prefixes    list[str]
#           sort_key   callable      default=${{_default_sort_key}}
include_empty_files    bool          default=False
include_resource_forks bool          default=False
 include_soft_links    bool          default=False
    ignore_filename    str
'''

  #@abstractmethod
  def _variables(self):
    return self.combine_variables(super()._variables(), {
      '_default_sort_key': lambda: bf_file_dups_finder_options.mtime_sort_key,
    })
  
class bf_file_dups_finder_options(bcli_options):
  def __init__(self, **kwargs):
    super().__init__(_bf_file_dups_finder_options_desc(), **kwargs)

  @staticmethod
  def sort_key_modification_date(filename):
    return ( file_util.get_modification_date(filename), )

  @staticmethod
  def sort_key_basename_length(filename):
    return ( len(path.basename(filename)),  )

  @staticmethod
  def mtime_sort_key(filename):
    mtime = bf_file_dups_finder_options.sort_key_modification_date(filename)
    length = bf_file_dups_finder_options.sort_key_basename_length(filename)
    return ( mtime, length )

  def pass_through_keys(self):
    return ( 'file_resolver_options', )

  @property
  def file_resolver_options(self):
    return bf_file_resolver_options(file_type = self.file_type,
                                    max_depth = self.max_depth,
                                    min_depth = self.min_depth,
#                                    sort_order = self.sort_order,
                                    ignore_filename = self.ignore_filename,
                                    entry_list_class = bf_file_dups_entry_list,
                                    include_resource_forks = self.include_resource_forks)
  
bf_file_dups_finder_options.register_check_class()
