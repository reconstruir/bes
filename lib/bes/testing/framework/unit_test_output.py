#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import re
from collections import namedtuple

class unit_test_output(object):

  _error = namedtuple('_error', 'error_type, fixture, function')
  _error_status = namedtuple('_error_status', 'num_errors, num_failures, errors')
  
  @classmethod
  def error_status(clazz, output):
    num_errors = 0
    num_failures = 0
    errors = []
    for line in reversed(output.split('\n')):
      for error_type in [ 'FAIL', 'ERROR' ]:
        exp = r'^\s*%s:\s+(.+)\s+\(__main__\.(.+)\)\s*$' % (error_type)
        r = re.findall(exp, line)
        if r:
          fixture = r[0][1]
          function = r[0][0]
          errors.append(clazz._error(error_type, r[0][1], r[0][0]))
          if error_type == 'FAIL':
            num_failures += 1
          elif error_type == 'ERROR':
            num_errors += 1
    return clazz._error_status(num_errors, num_failures, errors)
