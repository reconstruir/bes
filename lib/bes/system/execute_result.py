# -*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import locale
import sys

from collections import namedtuple

from .check import check
from .log import log

class execute_result(namedtuple('execute_result', 'stdout_bytes, stderr_bytes, exit_code, command')):
  'Class to deal with the result of execute.execute()'

  DEFAULT_ENCODING = locale.getpreferredencoding(False)
  
  def __new__(clazz, stdout_bytes, stderr_bytes, exit_code, command):
    check.check_bytes(stdout_bytes)
    check.check_bytes(stderr_bytes)
    check.check_int(exit_code)
    check.check_string_seq(command)

    return clazz.__bases__[0].__new__(clazz, stdout_bytes, stderr_bytes, exit_code, command)

#  def __str__(self):
#    ss = '-' if self.is_pointer else '*'
#    return '{} {} {}'.format(self.oid, ss, self.filename)

  @property
  def stdout(self):
    return self.stdout_bytes.decode(self.DEFAULT_ENCODING, errors = 'replace')

  @property
  def stderr(self):
    return self.stderr_bytes.decode(self.DEFAULT_ENCODING, errors = 'replace')
  
  def stdout_lines(self):
    'Return stdout as stripped lines'
    lines = [ line.strip() for line in self.stdout.splitlines() ]
    lines = [ line for line in lines if line ]
    return lines

  def stderr_lines(self):
    'Return stderr as stripped lines'
    lines = [ line.strip() for line in self.stderr.splitlines() ]
    lines = [ line for line in lines if line ]
    return lines
  
  def raise_error(self, print_error = False, log_error = False, tag = None):
    # FIXME: check if stdout is printable
    if log_error:
      self.log_error(tag = tag)
    if print_error:
      self.print_error()
    ex = RuntimeError(self.stdout)
    setattr(ex, 'execute_result', self)
    raise ex

  def print_error(self):
    sys.stdout.write('  command: {}'.format(self._command_to_string()))
    sys.stdout.write('exit_code: {}\n'.format(self.exit_code))
    sys.stdout.write('   stderr: {}\n'.format(self.stderr))
    sys.stdout.write('   stdout: {}\n'.format(self.stdout))
    sys.stdout.flush()
  
  def log_error(self, tag = None):
    tag = tag or 'execute'
    log.log_d(tag, '  command: {}'.format(self._command_to_string()))
    log.log_d(tag, 'exit_code: {}'.format(self.exit_code))
    log.log_d(tag, '   stderr: {}'.format(self.stderr))
    log.log_d(tag, '   stdout: {}'.format(self.stdout))

  def _command_to_string(self):
    if check.is_string(self.command):
      return self.command
    return ' '.join(self.command)

  @property
  def succeeded(self):
    return self.exit_code == 0

  @property
  def failed(self):
    return self.exit_code != 0
  
check.register_class(execute_result)
