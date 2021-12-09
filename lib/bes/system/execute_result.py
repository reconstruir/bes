# -*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

from bes.common.check import check

class execute_result(namedtuple('execute_result', 'stdout, stderr, exit_code, command')):
  'Class to deal with the result of execute.execute()'

  def __new__(clazz, stdout, stderr, exit_code, command):
    check.check_string(stdout)
    check.check_string(stderr, allow_none = True)
    check.check_int(exit_code)
    check.check_string_seq(command)

    return clazz.__bases__[0].__new__(clazz, stdout, stderr, exit_code, command)

#  def __str__(self):
#    ss = '-' if self.is_pointer else '*'
#    return '{} {} {}'.format(self.oid, ss, self.filename)

check.register_class(execute_result)
