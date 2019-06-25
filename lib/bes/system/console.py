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
    devices = clazz._possible_devices()
    fout = clazz._open_console(devices)
    if fout:
      try:
        clazz._output_stream(fout, message)
      except Exception as ex:
        pass
      finally:
        fout.close()

  _WINDOWS_DEVICES = [ 'con:' ]
  _UNIX_DEVICES = [ '/dev/console', '/dev/tty' ]
  @classmethod
  def _possible_devices(clazz):
    if host.is_windows():
      return clazz._WINDOWS_DEVICES
    elif host.is_unix():
      return clazz._UNIX_DEVICES
    return []

  @classmethod
  def _open_console(clazz, devices):
    for dev in devices:
      try:
        f = open(dev, 'w')
        return f
      except Exception as ex:
        pass
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
