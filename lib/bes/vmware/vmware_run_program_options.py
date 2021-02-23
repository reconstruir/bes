#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common.check import check
from bes.cli.cli_options import cli_options

from .vmware_error import vmware_error

class vmware_run_program_options(cli_options):
  
  def __init__(self, **kargs):
    super(vmware_run_program_options, self).__init__(**kargs)

  @classmethod
  #@abstractmethod
  def default_values(clazz):
    'Return a dict of defaults for these options.'
    return {
      'interactive': False,
      'no_wait': False,
      'active_window': False,
      'tail_log': False,
      'output_filename': None,
    }
  
  @classmethod
  #@abstractmethod
  def sensitive_keys(clazz):
    'Return list of keys that are secrets and should be protected from __str__.'
    return None
  
  @classmethod
  #@abstractmethod
  def value_type_hints(clazz):
    return {
      'interactive': bool,
      'no_wait': bool,
      'active_window': bool,
      'tail_log': bool,
    }

  @classmethod
  #@abstractmethod
  def config_file_key(clazz):
    return None

  @classmethod
  #@abstractmethod
  def config_file_section(clazz):
    return None

  @classmethod
  #@abstractmethod
  def error_class(clazz):
    return vmware_error

  #@abstractmethod
  def check_value_types(self):
    'Check the type of each option.'
    check.check_bool(self.interactive)
    check.check_bool(self.no_wait)
    check.check_bool(self.active_window)
    check.check_bool(self.tail_log)
    check.check_string(self.output_filename, allow_none = True)

  def to_vmrun_command_line_args(self):
    args = []
    if self.interactive:
      args.append('-interactive')
    if self.no_wait:
      args.append('-noWait')
    if self.active_window:
      args.append('-activeWindow')
    return args
    
check.register_class(vmware_run_program_options)