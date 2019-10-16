#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import shlex
from .compat import compat
from .host import host

class command_line(object):
  'command_line'

  @classmethod
  def parse_args(clazz, args):
    'Parse arguments to use for execute.'
    if host.SYSTEM == host.WINDOWS:
      return clazz._parse_args_windows(args)
    else:
      return clazz._parse_args_unix(args)
    
  @classmethod
  def _parse_args_unix(clazz, args):
    if compat.is_string(args):
      return shlex.split(args)
    elif isinstance(args, list):
      return args
    else:
      raise TypeError('args should be a string or list of strings instead of: {}'.format(args))
    
  @classmethod
  def _parse_args_windows(clazz, args):
    if compat.is_string(args):
      return clazz.win_CommandLineToArgvW(args)
    elif isinstance(args, list):
      return args
    else:
      raise TypeError('args should be a string or list of strings instead of: {}'.format(args))
    
  @classmethod
  def win_CommandLineToArgvW(clazz, cmd):
    import ctypes
    nargs = ctypes.c_int()
    ctypes.windll.shell32.CommandLineToArgvW.restype = ctypes.POINTER(ctypes.c_wchar_p)
    lpargs = ctypes.windll.shell32.CommandLineToArgvW(cmd, ctypes.byref(nargs))
    args = [lpargs[i] for i in range(nargs.value)]
    if ctypes.windll.kernel32.LocalFree(lpargs):
      raise AssertionError
    return args
  
  @classmethod
  def listify(clazz, command):
    'Listify a command if needed'
    if isinstance(command, ( list )):
      return command
    else:
      return shlex.split(str(command))
