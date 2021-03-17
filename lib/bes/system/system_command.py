#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import re

from abc import abstractmethod, ABCMeta
from bes.system.compat import with_metaclass

from .command_line import command_line
from .compat import compat
from .execute import execute
from .which import which

class system_command(with_metaclass(ABCMeta, object)):
  'Abstract base class for dealing with system commands.'
  
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

  def call_command(self, args, raise_error = True):
    'Call the command'
    if isinstance(args, ( list, tuple )):
      parsed_args = list(args)
    elif isinstance(args, compat.STRING_TYPES):
      parsed_args = command_line.parse_args(args)
    else:
      raise TypeError('Invalid args type.  Should be tuple, list or string: {} - {}'.format(args,
                                                                                            type(args)))

    exe = self._find_exe()
    static_args = self.static_args() or []
    if not isinstance(static_args, ( list, tuple )):
      raise TypeError('Return value of static_args() should be list or tuple: {} - {}'.format(static_args,
                                                                                              type(static_args)))
    cmd = [ exe ] + list(static_args) + args
    return execute.execute(cmd, raise_error = raise_error)

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
