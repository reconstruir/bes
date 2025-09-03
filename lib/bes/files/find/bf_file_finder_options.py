#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.bcli.bcli_options import bcli_options
from bes.bcli.bcli_options_desc import bcli_options_desc

from bes.system.check import check
from bes.property.cached_property import cached_property

from ..match.bf_file_matcher_mode import bf_file_matcher_mode
from ..match.bf_file_matcher_mode import bf_cli_file_matcher_mode
from ..match.bf_file_matcher import bf_cli_match
from ..match.bf_file_matcher import bf_file_matcher

from ..bf_path_type import bf_path_type
from ..bf_path_type import bf_cli_path_type
from ..bf_file_type import bf_file_type
from ..bf_file_type import bf_cli_file_type
from ..bf_entry import bf_entry

from .bf_file_finder_error import bf_file_finder_error
from .bf_file_finder_progress import bf_file_finder_progress
from .bf_file_finder_progress_state import bf_file_finder_progress_state
from .bf_file_finder_mode import bf_file_finder_mode
from .bf_file_finder_mode import bf_cli_file_finder_mode

class _bf_file_finder_options_desc(bcli_options_desc):

  #@abstractmethod
  def _types(self):
    return [
      bf_cli_file_matcher_mode,
      bf_cli_file_type,
      bf_cli_match,
      bf_cli_path_type,
      bf_cli_file_finder_mode,
    ]

  #@abstractmethod
  def _variables(self):
    return {
      '_bf_file_finder_entry_default_type': lambda: bf_entry,
    }
  
  #@abstractmethod
  def _options_desc(self):
    return '''
                match_type bf_file_matcher_mode default=ANY
                 file_type bf_file_type         default=FILE_OR_LINK
              follow_links bool                 default=False
       ignore_broken_links bool                 default=True
                 max_depth int
                 min_depth int
              file_matcher bf_file_matcher 
          walk_dir_matcher bf_file_matcher 
       walk_dir_match_type bf_file_matcher_mode default=ANY
                     limit int
             stop_function callable
#         progress_function callable
# progress_interval_percent float                default=5.0
                stop_after int
            found_callback callable
               entry_class type                 default=${_bf_file_finder_entry_default_type}
          ignore_filenames list[str]
                      mode bf_file_finder_mode  default=WITH_PROGRESS
'''
  
  #@abstractmethod
  def _error_class(self):
    return bf_file_finder_error
  
class bf_file_finder_options(bcli_options):
  def __init__(self, **kwargs):
    super().__init__(_bf_file_finder_options_desc(), **kwargs)

  def init_hook(self):
    self._check_depth_limits()

  def setattr_hook(self, name):
    if name in ( 'min_depth', 'max_depth' ):
      self._check_depth_limits()

  def pass_through_keys(self):
    return ( 'file_resolver_options', )

  @cached_property
  def file_ignore_list(self):
    if self.ignore_filenames:
      from ..ignore.bf_file_ignore_list import bf_file_ignore_list
      return bf_file_ignore_list(self.ignore_filenames)
    return None

  def should_ignore_entry(self, entry):
    if self.file_ignore_list:
      return self.file_ignore_list.should_ignore(entry)
    
  def _check_depth_limits(self):
    if self.max_depth and self.min_depth and not (self.max_depth >= self.min_depth):
      raise bf_file_finder_error('max_depth needs to be >= min_depth.')

    if self.min_depth and self.min_depth < 1:
      raise bf_file_finder_error('min_depth needs to be >= 1.')
  
  def depth_in_range(self, depth):
    if self.min_depth and self.max_depth:
      return depth >= self.min_depth and depth <= self.max_depth
    elif self.min_depth:
      return depth >= self.min_depth
    elif self.max_depth:
      return depth <= self.max_depth
    return True

  def file_matcher_matches(self, entry):
    check.check_bf_entry(entry)
    
    if not self.file_matcher:
      return True
    return self.file_matcher.match(entry, self.match_type)
    
  def call_stop_function(self):
    if not self.stop_function:
      return False
    result = self.stop_function()
    if not check.is_bool(result):
      raise bf_file_finder_error(f'result from stop_function should be bool: "{result}" - {type(result)}')
    return result

#  def call_progress_function(self, state, index, total):
#    state = check.check_bf_file_finder_progress_state(state)
#    check.check_int(index, allow_none = True)
#    check.check_int(total, allow_none = True)
    
#    if not self.progress_function:
#      return
#    progress = bf_file_finder_progress(state, index, total)
#    self.progress_function(progress)
    
bf_file_finder_options.register_check_class()
