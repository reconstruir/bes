#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.cli.cli_options import cli_options
from bes.system.check import check
from bes.property.cached_property import cached_property

from ..match.bf_match_type import bf_match_type
from ..match.bf_match_options import bf_match_options

from ..bf_path_type import bf_path_type
from ..bf_file_type import bf_file_type

from .bf_find_error import bf_find_error
from .bf_find_progress import bf_find_progress
from .bf_find_progress_state import bf_find_progress_state

class bf_find_options(cli_options):

  def __init__(self, **kargs):
    super().__init__(**kargs)

  @classmethod
  #@abstractmethod
  def default_values(clazz):
    'Return a dict of defaults for these options.'
    return {
      'ignore_case': False,
      'match_type': bf_match_type.ANY,
      'path_type': bf_path_type.ABSOLUTE,
      'file_type': bf_file_type.FILE_OR_LINK,
      'follow_links': False,
      'ignore_case': False,
      'max_depth': None,
      'min_depth': None,
      'relative': True,
      'file_match': None,
      'limit': None,
      'stop_function': None,
      'progress_function': None,
      'progress_interval_percent': 5.0,
    }
  
  @classmethod
  #@abstractmethod
  def sensitive_keys(clazz):
    'Return a tuple of keys that are secrets and should be protected from __str__.'
    None
  
  @classmethod
  #@abstractmethod
  def value_type_hints(clazz):
    return {
      'relative': bool,
      'ignore_case': bool,
      'min_depth': int,
      'max_depth': int,
      'follow_links': bool,
      'limit': int,
      'stop_function': callable,
      'progress_function': callable,
      'progress_interval_percent': float,
    }

  @classmethod
  #@abstractmethod
  def config_file_key(clazz):
    return None

  @classmethod
  #@abstractmethod
  def config_file_env_var_name(clazz):
    return None
  
  @classmethod
  #@abstractmethod
  def config_file_section(clazz):
    return None

  @classmethod
  #@abstractmethod
  def error_class(clazz):
    return RuntimeError

  #@abstractmethod
  def check_value_types(self):
    'Check the type of each option.'
    check.check_bool(self.relative)
    check.check_bool(self.ignore_case)
    self.match_type = check.check_bf_match_type(self.match_type)
    self.path_type = check.check_bf_path_type(self.path_type)
    check.check_int(self.min_depth, allow_none = True)
    check.check_int(self.max_depth, allow_none = True)
    check.check_bool(self.follow_links)
    self.file_type = check.check_bf_file_type(self.file_type)
    check.check_bf_match(self.file_match, allow_none = True)
    check.check_int(self.limit, allow_none = True)
    check.check_callable(self.stop_function, allow_none = True)
    check.check_callable(self.progress_function, allow_none = True)
    check.check_number(self.progress_interval_percent)

    if self.max_depth and self.min_depth and not (self.max_depth >= self.min_depth):
      raise RuntimeError('max_depth needs to be >= min_depth.')

    if self.min_depth and self.min_depth < 1:
      raise RuntimeError('min_depth needs to be >= 1.')

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
  
check.register_class(bf_find_options)
