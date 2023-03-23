#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.cli.cli_options import cli_options
from bes.system.check import check
from bes.property.cached_property import cached_property

from ..match.bf_match_type import bf_match_type
from ..match.bf_match_options import bf_match_options

from ..bfile_path_type import bfile_path_type
from ..bfile_type import bfile_type

class bfile_finder_options(cli_options):

  def __init__(self, **kargs):
    super().__init__(**kargs)

  @classmethod
  #@abstractmethod
  def default_values(clazz):
    'Return a dict of defaults for these options.'
    return {
      'ignore_case': False,
      'match_type': bf_match_type.ANY,
      'path_type': bfile_path_type.ABSOLUTE,
      'file_type': bfile_type.FILE_OR_LINK,
      'follow_links': False,
      'ignore_case': False,
      'max_depth': None,
      'min_depth': None,
      'relative': True,
      'file_match': None,
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
    self.path_type = check.check_bfile_path_type(self.path_type)
    check.check_int(self.min_depth, allow_none = True)
    check.check_int(self.max_depth, allow_none = True)
    check.check_bool(self.follow_links)
    self.file_type = check.check_bfile_type(self.file_type)
    check.check_bf_match(self.file_match, allow_none = True)

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
    check.check_bfile_entry(entry)
    
    if not self.file_match:
      return True
    return self.file_match.match(entry, self.matcher_options)
    
check.register_class(bfile_finder_options)
