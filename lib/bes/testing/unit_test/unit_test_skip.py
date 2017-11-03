#!/usr/bin/env python
#-*- coding:utf-8 -*-

# Borrowed from: http://stackoverflow.com/questions/21936292/conditional-skip-testcase-decorator-in-nosetests

import functools, unittest, types
from bes.system import host, compat

def _id(obj):
  return obj

def skip(reason):
  """Unconditionally skip a test."""
  def decorator(test_item):
    if not isinstance(test_item, compat.CLASS_TYPES):
      @functools.wraps(test_item)
      def skip_wrapper(*args, **kwargs):
        raise unittest.SkipTest(reason)
      test_item = skip_wrapper
    elif issubclass(test_item, unittest.TestCase):
      @classmethod
      @functools.wraps(test_item.setUpClass)
      def skip_wrapper(*args, **kwargs):
        raise unittest.SkipTest(reason)
      test_item.setUpClass = skip_wrapper
    test_item.__unittest_skip__ = True
    test_item.__unittest_skip_why__ = reason
    return test_item
  return decorator

def skip_if(condition, reason, warning = False):
  """Skip a test if the condition is true."""
  if condition:
    if warning:
      print('SKIPPED: %s' % (reason))
    return skip(reason)
  return _id

def raise_skip_if(conditional, message):
  if not conditional:
    raise unittest.SkipTest(message)

def raise_skip_if_not_platform(system):
  raise_skip_if(not host.SYSTEM != system, 'not %s' % (system))
