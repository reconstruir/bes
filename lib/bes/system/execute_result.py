# -*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import locale

from collections import namedtuple

from bes.common.check import check

class execute_result(namedtuple('execute_result', 'stdout_bytes, stderr_bytes, exit_code, command')):
  'Class to deal with the result of execute.execute()'

  _DEFAULT_ENCODING = locale.getpreferredencoding(False)
  
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
    return self.stdout_bytes.decode(self._DEFAULT_ENCODING, errors = 'replace')

  @property
  def stderr(self):
    return self.stderr_bytes.decode(self._DEFAULT_ENCODING, errors = 'replace')
  
  def stdout_lines(self):
    'Return stdout as stripped lines'
    lines = [ line.strip() for line in self.stdout.splitlines() ]
    lines = [ line for line in lines if line ]
    return lines

check.register_class(execute_result)
