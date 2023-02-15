#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

import re
import subprocess
import time

from .check import check
from .log import logger
from .system_error import system_error

class system_popen(object):

  _log = logger('popen')

  def __init__(self, process):
    check.check(process, subprocess.Popen)

    self._process = process

  @property
  def pid(self):
    return self._process.pid
    
  @property
  def stdout(self):
    return self._process.stdout

  @property
  def stderr(self):
    return self._process.stderr

  def next_stdout_line(self):
    return self._process.stdout.readline().strip().decode()

  def wait(self):
    return self._process.wait()
  
  _expect_result = namedtuple('_expect_result', 'result, pattern')
  def expect(self, pattern, raise_error = True, num_tries = 10, sleep_time = 1.0):
    check.check_bool(raise_error)
    check.check_int(num_tries)
    check.check_number(sleep_time)

    if check.is_string_seq(pattern):
      patterns = pattern
    elif check.is_string(pattern):
      patterns = [ pattern ]
    else:
      raise ValueError(f'pattern should be a string or string sequence: "{pattern}"')
    
    for try_number in range(1, num_tries + 1):
      next_line = self.next_stdout_line()
      self._log.log_d(f'next_line="{next_line}"')
      if not next_line:
        continue
      result, pattern = self._parse_patterns(patterns, next_line)
      if result != None:
        return self._expect_result(result, pattern)
      time.sleep(sleep_time)
    if raise_error:
      raise system_error(f'Timed out expecting {pattern}')
    return None

  @classmethod
  def _parse_one_pattern(clazz, pattern, s):
    f = re.findall(pattern, s)
    if not f:
      return None
    if len(f) != 1:
      return None
    return f[0]

  @classmethod
  def _parse_patterns(clazz, patterns, s):
    for pattern in patterns:
      f = clazz._parse_one_pattern(pattern, s)
      if f != None:
        return f, pattern
    return None, None
  
check.register_class(system_popen, include_seq = False)
