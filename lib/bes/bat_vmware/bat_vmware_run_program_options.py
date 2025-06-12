#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from ..system.check import check
from bes.cli.cli_options import cli_options

from .bat_vmware_error import bat_vmware_error

class bat_vmware_run_program_options(cli_options):
  
  def __init__(self, **kargs):
    super(bat_vmware_run_program_options, self).__init__(**kargs)

  @classmethod
  #@abstractmethod
  def default_values(clazz):
    'Return a dict of defaults for these options.'
    return {
      'active_window': False,
      'clone_vm': False,
      'dont_ensure': False,
      'interactive': False,
      'no_wait': False,
      'output_filename': None,
      'tail_log': False,
      'wait_programs_num_tries': 60,
      'wait_programs_sleep_time': 2.0,
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
      'active_window': bool,
      'clone_vm': bool,
      'dont_ensure': bool,
      'interactive': bool,
      'no_wait': bool,
      'tail_log': bool,
      'wait_programs_num_tries': int,
      'wait_programs_sleep_time': float,
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
    return bat_vmware_error

  #@abstractmethod
  def check_value_types(self):
    'Check the type of each option.'
    check.check_bool(self.interactive)
    check.check_bool(self.no_wait)
    check.check_bool(self.active_window)
    check.check_bool(self.tail_log)
    check.check_string(self.output_filename, allow_none = True)
    check.check_int(self.wait_programs_num_tries)
    check.check_float(self.wait_programs_sleep_time)
    check.check_bool(self.clone_vm)
    check.check_bool(self.dont_ensure)

  def to_vmrun_command_line_args(self):
    args = []
    if self.interactive:
      args.append('-interactive')
    if self.no_wait:
      args.append('-noWait')
    if self.active_window:
      args.append('-activeWindow')
    return args
    
check.register_class(bat_vmware_run_program_options)
