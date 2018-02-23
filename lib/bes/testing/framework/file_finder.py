#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import subprocess
from bes.text import lines
#from bes.fs import file_find, file_util

class file_finder(object):

  @classmethod
  def find_python_files(clazz, d):
    cmd = [ 'find', d, '-name', '*.py' ]
    result = subprocess.check_output(cmd, shell = False)
    return lines.parse_lines(result)

  @classmethod
  def find_tests(clazz, d):
    cmd = [ 'find', d, '-name', 'test_*.py' ]
    result = subprocess.check_output(cmd, shell = False)
    return lines.parse_lines(result)

#  @classmethod
#  def find(clazz, d, *args):
#    cmd = [ 'find', d ] + list(args)
#    result = subprocess.check_output(cmd, shell = False)
#    return lines.parse_lines(result)
