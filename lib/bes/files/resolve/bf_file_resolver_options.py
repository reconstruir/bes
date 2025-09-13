#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.bcli.bcli_options import bcli_options
from bes.bcli.bcli_options_desc import bcli_options_desc

from bes.system.check import check

from ..find.bf_file_finder_mode import bf_cli_file_finder_mode
from ..match.bf_file_matcher import bf_cli_file_matcher
from ..match.bf_file_matcher_mode import bf_cli_file_matcher_mode

from ..bf_entry_sort_criteria import bf_entry_sort_criteria_bcli
from ..bf_file_type import bf_cli_file_type

from .bf_file_resolver_entry import bf_file_resolver_entry

class _bf_file_resolver_options_desc(bcli_options_desc):

  #@abstractmethod
  def _types(self):
    return [
      bf_cli_file_finder_mode,
      bf_cli_file_matcher,
      bf_cli_file_matcher_mode,
      bf_cli_file_type,
      bf_entry_sort_criteria_bcli,
    ]

  #@abstractmethod
  def _variables(self):
    return {
      '_bf_file_resolver_entry_default_type': lambda: bf_file_resolver_entry,
    }
  
  #@abstractmethod
  def _options_desc(self):
    return '''
                 file_type bf_file_type            default=FILE_OR_LINK
                 max_depth int
                 min_depth int
                stop_after int
          walk_dir_matcher bf_file_matcher 
       walk_dir_match_type bf_file_matcher_mode    default=ANY
                      mode bf_file_finder_mode     default=IMMEDIATE
                sort_order bf_entry_sort_criteria  default=FILENAME
               entry_class type                    default=${_bf_file_resolver_entry_default_type}
            match_function callable
         progress_callback callable
 progress_interval_percent float                   default=5.0
           ignore_filename str
'''
  
  #@abstractmethod
  def _error_class(self):
    return bf_file_resolver_error
  
class bf_file_resolver_options(bcli_options):
  def __init__(self, **kwargs):
    super().__init__(_bf_file_resolver_options_desc(), **kwargs)

bf_file_resolver_options.register_check_class()
