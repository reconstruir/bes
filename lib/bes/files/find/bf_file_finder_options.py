#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.bcli.bcli_options import bcli_options
from bes.bcli.bcli_options_desc import bcli_options_desc

from bes.system.check import check

from ..match.bf_file_matcher import bf_cli_file_matcher

from ..bf_path_type import bf_cli_path_type

from .bf_file_finder_mode import bf_cli_file_finder_mode
from .bf_file_finder_progress import bf_file_finder_progress
from .bf_file_finder_progress_state import bf_file_finder_progress_state

from .bf_file_scanner_options import bf_file_scanner_options
from .bf_file_scanner_options import _bf_file_scanner_options_desc

class _bf_file_finder_options_desc(_bf_file_scanner_options_desc):

  #@abstractmethod
  def _types(self):
    return super()._types() + [
      bf_cli_file_finder_mode,
      bf_cli_path_type,
    ]

  #@abstractmethod
  def _options_desc(self):
    return self.combine_options_desc(super()._options_desc(), f'''
                match_type bf_file_matcher_mode default=ANY
              file_matcher bf_file_matcher 
#         progress_function callable
# progress_interval_percent float                default=5.0
            found_callback callable
                      mode bf_file_finder_mode  default=WITH_PROGRESS
''')

  
class bf_file_finder_options(bf_file_scanner_options):

  __desc_class__ = _bf_file_finder_options_desc
  
  def __init__(self, **kwargs):
    super().__init__(**kwargs)

#  def pass_through_keys(self):
#    return super().pass_through_keys() + ( 'file_ignore_list', )
#
#  @property
#  def file_scanner_options(self):
#    return bf_file_scanner_options()
  
  def file_matcher_matches(self, entry):
    check.check_bf_entry(entry)
    
    if not self.file_matcher:
      return True
    return self.file_matcher.match(entry, self.match_type)
    
#  def call_progress_function(self, state, index, total):
#    state = check.check_bf_file_finder_progress_state(state)
#    check.check_int(index, allow_none = True)
#    check.check_int(total, allow_none = True)
    
#    if not self.progress_function:
#      return
#    progress = bf_file_finder_progress(state, index, total)
#    self.progress_function(progress)
    
bf_file_finder_options.register_check_class()
