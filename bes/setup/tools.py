#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os, subprocess

class tools(object):
  'Tools to help deal with setup.py'
  
  _WANT_TESTS = bool(os.environ.get('BES_EGG_INCLUDE_TESTS', None))
  
  @classmethod
  def _find_tests(clazz, d):
    cmd = [ 'find', d, '-name', 'test_*.py' ]
    result = subprocess.check_output(cmd, shell = False)
    tests = [ test.strip() for test in result.strip().split('\n') if test.strip() ]
    tests = [ test[len(d)+1:] for test in tests ]
    return sorted(tests)
  
  @classmethod
  def find_tests(clazz, d):
    if not clazz._WANT_TESTS:
      return []
    return clazz._find_tests(d)
  
