#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.common import algorithm
from .unit_test_description import unit_test_description

import unittest

class unit_test_inspect(object):

  @classmethod
  def inspect_file(clazz, filename):
    try:
      return clazz.inspect_file_new(filename)
    except Exception as ex:
      print('WARNING: failed to inspect unit test %s: %s' % (path.relpath(filename), str(ex)))
      return None
  
  @classmethod
  def inspect_file_new(clazz, filename):
    loader = unittest.TestLoader()
    where = path.dirname(filename)
    pattern = path.basename(filename)
    discovery = loader.discover(where, pattern = pattern)
    result = []
    for disc in discovery:
      for suite in disc:
        for test in suite:
          fixture = test.__class__.__name__
          test_functions = loader.getTestCaseNames(test)
          for function in test_functions:
            result.append(unit_test_description(filename, fixture, function))
    return sorted(algorithm.unique(result), key = lambda x: x.function)
