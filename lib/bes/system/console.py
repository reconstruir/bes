#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path
import sys
from .host import host

class console(object):
  'Class to deal with the console in a cross platform manner.'

  @classmethod
  def output(clazz, message, console = False):
    if console:
      clazz._output_console(message)
    else:
      clazz._output_stream(sys.stdout, message)
  
  @classmethod
  def _output_console(clazz, message):
    dev = clazz._console_device()
    if not dev:
      raise IOError('console device not found for: {}'.format(host.SYSTEM))
    with open(dev, 'w') as fout:
      clazz._output_stream(fout, message)
      fout.close()

  _WINDOWS_CONSOLE = 'con:'
  _UNIX_DEVICES = [ '/dev/console', '/dev/tty' ]
      
  @classmethod
  def _console_device(clazz):
    if host.is_windows():
      return clazz._WINDOWS_CONSOLE
    elif host.is_unix():
      for dev in clazz._UNIX_DEVICES:
        if path.exists(dev):
          return dev
    return None

  @classmethod
  def _output_stream(clazz, stream, message):
    stream.write(message)
    if not clazz._ends_with_line_break(message):
      stream.write(clazz._DEFAULT_LINE_BREAK)
    stream.flush()

  _LINE_BREAKS = [ '\n', '\r\n' ]
  _DEFAULT_LINE_BREAK = '\n' if host.is_unix() else '\r\n'

  @classmethod
  def _ends_with_line_break(clazz, s):
    for lb in clazz._LINE_BREAKS:
      if s.endswith(lb):
        return True
    return False
