#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from bes.common.algorithm import algorithm

from .pytest import pytest

import unittest

class unit_test_inspect(object):

  @classmethod
  def inspect_file(clazz, filename):
    result = []    
    try:
      result = pytest.inspect_file(filename)
    except Exception as ex:
      print('WARNING: failed to inspect unit test %s: %s' % (path.relpath(filename), str(ex)))
      raise
      #return None
    return sorted(algorithm.unique(result), key = lambda x: ( x.fixture, x.function ))
