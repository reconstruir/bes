#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.bcli.bcli_options import bcli_options
from bes.bcli.bcli_options_desc import bcli_options_desc

from bes.bcli.bcli_type_i import bcli_type_i

from bes.cli.cli_options import cli_options
from ..system.check import check
from bes.common.time_util import time_util
from bes.fs.file_ignore_options_mixin import file_ignore_options_mixin
from bes.property.cached_property import cached_property

from .file_resolver_options import file_resolver_options

class files_cli_options(cli_options, file_ignore_options_mixin):

  def __init__(self, **kargs):
    super().__init__(**kargs)

  @classmethod
  #@abstractmethod
  def default_values(clazz):
    'Return a dict of defaults for these options.'
    return {
      'debug': False,
      'dry_run': False,
      'quiet': False,
      'recursive': False,
      'verbose': False,
      'ignore_files': None,
      'dup_file_timestamp': time_util.timestamp(),
      'dup_file_count': 1,
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
      'debug': bool,
      'dry_run': bool,
      'quiet': bool,
      'recursive': bool,
      'verbose': bool,
      'ignore_files': list,
      'dup_file_count': int,
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
    return IOError

  #@abstractmethod
  def check_value_types(self):
    'Check the type of each option.'
    check.check_bool(self.debug)
    check.check_bool(self.dry_run)
    check.check_bool(self.quiet)
    check.check_bool(self.recursive)
    check.check_bool(self.verbose)
    check.check_string_seq(self.ignore_files, allow_none = True)
    check.check_string(self.dup_file_timestamp, allow_none = True)
    check.check_int(self.dup_file_count, allow_none = True)

  @cached_property
  def file_resolver_options(self):
    return file_resolver_options(recursive = self.recursive,
                                 ignore_files = self.ignore_files)
    
check.register_class(files_cli_options)
