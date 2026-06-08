#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os, subprocess

from bes.files.bf_filename import bf_filename

class tools(object):
  'Tools to help deal with setup.py'

  _TEST_FILE_PATTERNS = [ '*/tests/*.py*', '*/test_data/*', '*/bes_test.py' ]
  _WANT_TESTS = bool(os.environ.get('BES_EGG_INCLUDE_TESTS', None))

  @classmethod
  def find_tests(clazz, d):
    import fnmatch
    cmd = [ 'find', d, '-type', 'f' ]
    rv = subprocess.check_output(cmd, shell = False)
    files = [ f.strip() for f in rv.split('\n') if f.strip() ]
    tests = [ f for f in files if any(fnmatch.fnmatch(f, p) for p in clazz._TEST_FILE_PATTERNS) ]
    return sorted([ bf_filename.remove_head(f, d) for f in tests ])

  @classmethod
  def want_tests(clazz):
    return clazz._WANT_TESTS

  @classmethod
  def find_tests_if_wanted(clazz, d):
    if not clazz.want_tests():
      return []
    return clazz.find_tests(d)
