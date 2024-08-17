#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.bcli.bcli_options import bcli_options
from bes.bcli.bcli_options_desc import bcli_options_desc

from bes.system.check import check
from bes.property.cached_property import cached_property

from ..match.bf_match_type import bf_match_type
from ..match.bf_match_type import bf_cli_match_type
from ..match.bf_match_options import bf_match_options
from ..match.bf_match import bf_cli_match

from ..bf_path_type import bf_path_type
from ..bf_path_type import bf_cli_path_type
from ..bf_file_type import bf_file_type
from ..bf_file_type import bf_cli_file_type

from .bf_find_error import bf_find_error
from .bf_find_progress import bf_find_progress
from .bf_find_progress_state import bf_find_progress_state

class _bf_find_options_desc(bcli_options_desc):

  #@abstractmethod
  def types(self):
    return [
      bf_cli_file_type,
      bf_cli_match,
      bf_cli_match_type,
      bf_cli_path_type,
    ]
  
  #@abstractmethod
  def options_desc(self):
    return '''
               ignore_case bool          default=False
                match_type bf_match_type default=ANY
                 path_type bf_path_type  default=ABSOLUTE
                 file_type bf_file_type  default=FILE|LINK
              follow_links bool          default=False
                 max_depth int
                 min_depth int
                  relative bool          default=True
                file_match bf_match
                     limit int
             stop_function callable
         progress_function callable
 progress_interval_percent float         default=5.0
'''
  
class bf_find_options(bcli_options):
  def __init__(self, **kwargs):
    super().__init__(_bf_find_options_desc(), **kwargs)

  def init_hook(self):
    self._check_depth_limits()

  def setattr_hook(self, name):
    if name in ( 'min_depth', 'max_depth' ):
      self._check_depth_limits()

  def _check_depth_limits(self):
    if self.max_depth and self.min_depth and not (self.max_depth >= self.min_depth):
      raise RuntimeError('max_depth needs to be >= min_depth.')

    if self.min_depth and self.min_depth < 1:
      raise RuntimeError('min_depth needs to be >= 1.')
  
  def pass_through_keys(self):
    return ( 'matcher_options', )
    
  def depth_in_range(self, depth):
    if self.min_depth and self.max_depth:
      return depth >= self.min_depth and depth <= self.max_depth
    elif self.min_depth:
      return depth >= self.min_depth
    elif self.max_depth:
      return depth <= self.max_depth
    return True

  @cached_property
  def matcher_options(self):
    return bf_match_options(ignore_case = self.ignore_case,
                            match_type = self.match_type,
                            path_type = self.path_type)
  
  def file_match_matches(self, entry):
    check.check_bf_entry(entry)
    
    if not self.file_match:
      return True
    return self.file_match.match(entry, self.matcher_options)
    
  def call_stop_function(self):
    if not self.stop_function:
      return False
    result = self.stop_function()
    if not check.is_bool(result):
      raise bf_find_error(f'result from stop_function should be bool: "{result}" - {type(result)}')
    return result

  def call_progress_function(self, state, index, total):
    state = check.check_bf_find_progress_state(state)
    check.check_int(index, allow_none = True)
    check.check_int(total, allow_none = True)
    
    if not self.progress_function:
      return
    progress = bf_find_progress(state, index, total)
    self.progress_function(progress)
    
bf_find_options.register_check_class()
