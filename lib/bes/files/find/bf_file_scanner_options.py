#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.bcli.bcli_options import bcli_options
from bes.bcli.bcli_options_desc import bcli_options_desc

from bes.system.check import check

from ..match.bf_file_matcher import bf_cli_file_matcher
from ..match.bf_file_matcher_mode import bf_cli_file_matcher_mode

from ..bf_entry import bf_entry
from ..bf_entry_list import bf_entry_list
from ..bf_file_type import bf_cli_file_type

from .bf_file_finder_error import bf_file_finder_error
from .bf_file_finder_mode import bf_cli_file_finder_mode

class _bf_file_scanner_options_desc(bcli_options_desc):

  #@abstractmethod
  def _types(self):
    return [
      bf_cli_file_matcher,
      bf_cli_file_matcher_mode,
      bf_cli_file_type,
    ]

  #@abstractmethod
  def _variables(self):
    return {
      '_bf_file_scanner_entry_default_type': lambda: bf_entry,
      '_bf_file_scanner_entry_list_default_type': lambda: bf_entry_list,
    }
  
  #@abstractmethod
  def _options_desc(self):
    return '''
                 file_type bf_file_type         default=FILE_OR_LINK
              follow_links bool                 default=False
       ignore_broken_links bool                 default=True
                 max_depth int
                 min_depth int
          walk_dir_matcher bf_file_matcher 
       walk_dir_match_type bf_file_matcher_mode default=ANY
             stop_function callable
                stop_after int
          file_entry_class type                 default=${_bf_file_scanner_entry_default_type}
           dir_entry_class type                 default=${_bf_file_scanner_entry_default_type}
          entry_list_class type                 default=${_bf_file_scanner_entry_list_default_type}
           ignore_filename str
    include_resource_forks bool                 default=False
'''
  
  #@abstractmethod
  def _error_class(self):
    return bf_file_finder_error
  
class bf_file_scanner_options(bcli_options):

  __desc_class__ = _bf_file_scanner_options_desc
  
  def __init__(self, **kwargs):
    super().__init__(self.__desc_class__(), **kwargs)

  def init_hook(self):
    self._check_depth_limits()

  def setattr_hook(self, name):
    if name in ( 'min_depth', 'max_depth' ):
      self._check_depth_limits()

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

  def call_stop_function(self):
    if not self.stop_function:
      return False
    result = self.stop_function()
    if not check.is_bool(result):
      raise bf_file_finder_error(f'result from stop_function should be bool: "{result}" - {type(result)}')
    return result
    
bf_file_scanner_options.register_check_class()
