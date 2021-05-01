#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path
import os, sys
import subprocess

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
  _UNIX_DEVICES = [ '/dev/tty', '/dev/console' ]
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

  @classmethod
  def terminal_device(clazz):
    'Return the current terminal device or None if not a terminal.'
    if host.is_windows():
      return False
    elif host.is_unix():
      try:
        dev = subprocess.check_outpout('tty').stdout.strip()
        with open(dev, 'r') as f:
          if os.isatty(f.fileno()):
            return dev
          else:
            return None
      except Exception as ex:
        print(ex)
        return None
    else:
      host.raise_unsupported_system()

  @classmethod
  def terminal_size(clazz):
    'Return a 2-tuple ( width, height ) size of the current terminal or None if not a terminal.'
    dev = clazz.terminal_device()
    if not dev:
      return None
    assert host.is_unix() # for now only unix
    try:
      with open(dev, 'r') as f:
        cmd = 'stty size < {}'.format(dev)
        s = os.popen(cmd, 'r').read().split()
        return int(s[1]), int(s[0])
    except Exception as ex:
      print(ex)
      return None

  @classmethod
  def terminal_width(clazz, default = 80):
    'Return the terminal width or None if not a terminal'
    s = clazz.terminal_size()
    return s[0] if s else default

  @classmethod
  def terminal_heigh(clazz, default = 36):
    'Return the terminal width or None if not a terminal'
    s = clazz.terminal_size()
    return s[1] if s else default
