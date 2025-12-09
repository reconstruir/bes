#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import re
from os import path

from abc import abstractmethod, ABCMeta

from .check import check
from .command_line import command_line
from .compat import compat
from .env_override import env_override
from .env_override_options import env_override_options
from .execute import execute
from .execute_result import execute_result
from .host import host
from .log import logger
from .system_popen import system_popen
from .which import which

class system_command(object, metaclass = ABCMeta):
  'Abstract base class for dealing with system commands.'

  _log = logger('system_command')
  
  @classmethod
  @abstractmethod
  def exe_name(clazz):
    'The name of the executable.'
    raise NotImplementedError('exe_name')

  @classmethod
  @abstractmethod
  def extra_path(clazz):
    'List of extra paths where to find the command.'
    raise NotImplementedError('extra_path')

  @classmethod
  @abstractmethod
  def error_class(clazz):
    'The error exception class to raise when errors happen.'
    raise NotImplementedError('error_class')

  @classmethod
  @abstractmethod
  def static_args(clazz):
    'List of static arg for all calls of the command.'
    raise NotImplementedError('static_args')

  @classmethod
  @abstractmethod
  def supported_systems(clazz):
    'Return a list of supported systems.'
    raise NotImplementedError('supported_systems')
  
  @classmethod
  def _find_exe(clazz):
    'Find the exe'
    exe_name = clazz.exe_name()
    if path.isabs(exe_name):
      exe = exe_name
    else:
      exe = which.which(exe_name, extra_path = clazz.extra_path())
    if exe:
      return exe
    error_class = clazz.error_class()
    if not isinstance(error_class, Exception.__class__):
      raise TypeError('Return value of error_clas() should be an Exception type: {} - {}'.format(error_class,
                                                                                                 type(error_class)))
      
    raise error_class('Failed to find {}'.format(exe_name))

  @classmethod
  def call_command(clazz,
                   args,
                   raise_error = True,
                   env = None,
                   use_sudo = False,
                   stderr_to_stdout = False,
                   check_python_script = True,
                   input_data = None,
                   non_blocking = False,
                   output_encoding = None,
                   output_function = None,
                   env_options = None,
                   quote = True):
    'Call the command'
    check.check_string_seq(args)
    check.check_bool(raise_error)
    check.check_dict(env, check.STRING_TYPES, check.STRING_TYPES, allow_none = True)
    check.check_bool(use_sudo)
    check.check_bytes(input_data, allow_none = True)
    check.check_bool(non_blocking)
    check.check_string(output_encoding, allow_none = True)
    check.check_callable(output_function, allow_none = True)
    check.check_env_override_options(env_options, allow_none = True)
    check.check_bool(quote)

    clazz.check_supported()

    clazz._log.log_d('call_command: args={}'.format(' '.join(args)))
    
    if isinstance(args, ( list, tuple )):
      parsed_args = list(args)
    elif isinstance(args, compat.STRING_TYPES):
      parsed_args = command_line.parse_args(args)
    else:
      raise TypeError('Invalid args type.  Should be tuple, list or string: {} - {}'.format(args,
                                                                                            type(args)))
    clazz._log.log_d('call_command: parsed_args={}'.format(' '.join(parsed_args)))

    exe = clazz._find_exe()
    static_args = clazz.static_args() or []
    if not isinstance(static_args, ( list, tuple )):
      raise TypeError('Return value of static_args() should be list or tuple: {} - {}'.format(static_args,
                                                                                              type(static_args)))
    cmd = []
    if use_sudo:
      cmd.append('sudo')
    cmd.append(exe)
    cmd.extend(list(static_args))
    cmd.extend(args)
    clazz._log.log_d('call_command: cmd="{}" env="{}"'.format(' '.join(cmd), env))
    return execute.execute(cmd,
                           raise_error = raise_error,
                           env = env,
                           stderr_to_stdout = stderr_to_stdout,
                           check_python_script = check_python_script,
                           input_data = input_data,
                           non_blocking = non_blocking,
                           output_encoding = output_encoding,
                           env_options = env_options,
                           quote = quote)

  @classmethod
  def call_command_parse_lines(clazz, args, sort = False):
    'Call a command that returns a list of lines'
    rv = clazz.call_command(args, raise_error = True)
    result = clazz.split_lines(rv.stdout)
    if sort:
      result = sorted(result)
    return result

  @classmethod
  def is_supported(clazz):
    'Return True if this command is support on the current system'
    return host.SYSTEM in clazz.supported_systems()
  
  @classmethod
  def check_supported(clazz):
    'Check that the current system supports this command otherwise raise an error'
    if clazz.is_supported():
      return
    name = clazz.exe_name()
    systems = ' '.join(clazz.supported_systems())
    raise clazz.error_class()(f'{name} is not supported on {host.SYSTEM} - only {systems}')
  
  @classmethod
  def has_command(clazz):
    'Return True if the command is found'
    if not clazz.is_supported():
      return False
    try:
      exe = clazz._find_exe()
      return True
    except clazz.error_class() as ex:
      pass
    return False
  
  @classmethod
  def split_lines(clazz, text):
    lines = text.splitlines()
    lines = [ line.strip() for line in lines ]
    return [ line for line in lines if line ]

  @classmethod
  def split_by_white_space(clazz, line):
    parts = []
    for part in re.split(r'\s+', line):
      part = part.strip()
      if part:
        parts.append(part)
    return parts

  @classmethod
  def check_result(clazz, result, message = None):
    'Check that a result is successful or raise an exceptions from it.'
    check.check_string(message, allow_none = True)
    check.check_execute_result(result)
    
    if result.exit_code == 0:
      return
    message = message or 'Failed to execute: {}'.format(' '.join(result.command))
    outputs = [ o.strip() for o in [ result.stdout, result.stderr ] if o.strip() ]
    error_message = '{} - {}'.format(message, ' - '.join(outputs))
    raise clazz.error_class()(error_message)

  @classmethod
  def popen(clazz,
            args = [],
            env = None,
            use_sudo = False,
            stderr_to_stdout = False,
            check_python_script = True,
            input_data = None,
            env_options = None):
    'Call execute.popen()'
#    check.check_string_seq(args)
#    check.check_dict(env, check.STRING_TYPES, check.STRING_TYPES, allow_none = True)
#    check.check_bool(use_sudo)
#    check.check_bytes(input_data, allow_none = True)
#    check.check_env_override_options(env_options, allow_none = True)

    clazz.check_supported()

    clazz._log.log_d(f'call_command: args={args}')
    
    if isinstance(args, ( list, tuple )):
      parsed_args = list(args)
    elif isinstance(args, compat.STRING_TYPES):
      parsed_args = command_line.parse_args(args)
    else:
      raise TypeError('Invalid args type.  Should be tuple, list or string: {} - {}'.format(args,
                                                                                            type(args)))
    clazz._log.log_d('call_command: parsed_args={}'.format(' '.join(parsed_args)))

    exe = clazz._find_exe()
    static_args = clazz.static_args() or []
    if not isinstance(static_args, ( list, tuple )):
      raise TypeError('Return value of static_args() should be list or tuple: {} - {}'.format(static_args,
                                                                                              type(static_args)))
    cmd = []
    if use_sudo:
      cmd.append('sudo')
    cmd.append(exe)
    cmd.extend(list(static_args))
    cmd.extend(args)
    clazz._log.log_d('call_command: cmd={} env={}'.format(' '.join(cmd), env))
    process = execute.popen(cmd,
                            env = env,
                            stderr_to_stdout = stderr_to_stdout,
                            check_python_script = check_python_script,
                            input_data = input_data,
                            env_options = env_options)
    return system_popen(process)
  
check.register_class(system_command, include_seq = False)
