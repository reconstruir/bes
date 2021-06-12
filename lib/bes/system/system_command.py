#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import re

from abc import abstractmethod, ABCMeta
from bes.system.compat import with_metaclass

from .check import check
from .command_line import command_line
from .compat import compat
from .execute import execute
from .host import host
from .log import logger
from .which import which

class system_command(with_metaclass(ABCMeta, object)):
  'Abstract base class for dealing with system commands.'

  _log = logger('system_command')
  
  @abstractmethod
  def exe_name(self):
    'The name of the executable.'
    raise NotImplemented('exe_name')

  @abstractmethod
  def extra_path(self):
    'List of extra paths where to find the command.'
    raise NotImplemented('extra_path')

  @abstractmethod
  def error_class(self):
    'The error exception class to raise when errors happen.'
    raise NotImplemented('error_class')

  @abstractmethod
  def static_args(self):
    'List of static arg for all calls of the command.'
    raise NotImplemented('static_args')

  @abstractmethod
  def supported_systems(self):
    'Return a list of supported systems.'
    raise NotImplemented('supported_systems')
  
  def _find_exe(self):
    'Find the exe'
    extra_path = self.extra_path()
    exe_name = self.exe_name()
    exe = which.which(exe_name, extra_path = self.extra_path())
    if exe:
      return exe
    error_class = self.error_class()
    if not isinstance(error_class, Exception.__class__):
      raise TypeError('Return value of error_clas() should be an Exception type: {} - {}'.format(error_class,
                                                                                                 type(error_class)))
      
    raise error_class('Failed to find {}'.format(exe_name))

  def call_command(self, args, raise_error = True, env = None, use_sudo = False):
    'Call the command'
    check.check_string_seq(args)
    check.check_bool(raise_error)
    check.check_dict(env, check.STRING_TYPES, check.STRING_TYPES, allow_none = True)
    check.check_bool(use_sudo)

    self.check_supported()

    self._log.log_d('call_command: args={}'.format(' '.join(args)))
    
    if isinstance(args, ( list, tuple )):
      parsed_args = list(args)
    elif isinstance(args, compat.STRING_TYPES):
      parsed_args = command_line.parse_args(args)
    else:
      raise TypeError('Invalid args type.  Should be tuple, list or string: {} - {}'.format(args,
                                                                                            type(args)))
    self._log.log_d('call_command: parsed_args={}'.format(' '.join(parsed_args)))

    exe = self._find_exe()
    static_args = self.static_args() or []
    if not isinstance(static_args, ( list, tuple )):
      raise TypeError('Return value of static_args() should be list or tuple: {} - {}'.format(static_args,
                                                                                              type(static_args)))
    cmd = []
    if use_sudo:
      cmd.append('sudo')
    cmd.append(exe)
    cmd.extend(list(static_args))
    cmd.extend(args)
    self._log.log_d('call_command: cmd={}'.format(' '.join(cmd)))
    return execute.execute(cmd, raise_error = raise_error, env = env)

  def call_command_parse_lines(self, args, sort = False):
    'Call a command that returns a list of lines'
    rv = self.call_command(args, raise_error = True)
    result = self.split_lines(rv.stdout)
    if sort:
      result = sorted(result)
    return result

  def is_supported(self):
    'Return True if this command is support on the current system'
    return host.SYSTEM in self.supported_systems()
  
  def check_supported(self):
    'Check that the current system supports this command otherwise raise an error'
    if self.is_supported():
      return
    raise error_class('{} is not supported on {} - only {}'.format(self.exe_name(),
                                                                   host.SYSTEM,
                                                                   ' '.join(self.supported_systems())))
  
  def has_command(self):
    'Return True if the command is found'
    if not self.is_supported():
      return False
    try:
      exe = self._find_exe()
      return True
    except self.error_class() as ex:
      pass
    return False
  
  @classmethod
  def split_lines(self, text):
    lines = text.splitlines()
    lines = [ line.strip() for line in lines ]
    return [ line for line in lines if line ]

  @classmethod
  def split_by_white_space(self, line):
    parts = []
    for part in re.split(r'\s+', line):
      part = part.strip()
      if part:
        parts.append(part)
    return parts
