#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import getpass

from bes.bcli.bcli_options import bcli_options
from bes.bcli.bcli_options_desc import bcli_options_desc

from ..bf_entry_sort_criteria import bf_entry_sort_criteria_bcli
from ..bf_file_type import bf_cli_file_type

from ..core.bf_files_cli_options import bf_files_cli_options
from ..core.bf_files_cli_options import _bf_files_cli_options_desc

from .bf_file_dups_finder_error import bf_file_dups_finder_error
from .bf_file_dups_finder_options import bf_file_dups_finder_options

class _bf_file_dups_command_options_desc(_bf_files_cli_options_desc):

  #@abstractmethod
  def _types(self):
    return [
      bf_cli_file_type,
      bf_entry_sort_criteria_bcli,
    ]
  
  #@abstractmethod
  def _options_desc(self):
    return '''
  verbose  bool         default=False
    debug  bool         default=False
    quiet  bool         default=False
  dry_run  bool         default=False
  stop_at  bool         default=False
     name  str
file_type  bf_file_type default=FILE_OR_LINK
max_depth  int
min_depth  int
stop_after int
sort_order bf_entry_sort_criteria  default=FILENAME
'''

  #@abstractmethod
  def _error_class(self):
    return bf_file_dups_finder_error
  
class bf_file_dups_command_options(bf_files_cli_options):
  def __init__(self, **kwargs):
    super().__init__(_bf_file_dups_command_options_desc(), **kwargs)

  def pass_through_keys(self):
    return ( 'file_duplicates_options', )
    
  @property
  def file_duplicates_options(self):
    return bf_file_dups_finder_options(file_type = self.file_type,
                                             max_depth = self.max_depth,
                                             min_depth = self.min_depth)
  
bf_file_dups_command_options.register_check_class()
