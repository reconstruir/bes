#!/usr/bin/env python
#-*- coding:utf-8 -*-
#

class FakeUnitTest(object):
  'A fake unit test class to make up for the missing one in android python.'
  class TestCase(object):
    def __init__(self): pass
    def assertEqual(self, a, b): pass

  @staticmethod
  def main(): pass

  @staticmethod
  def install():
    import sys
    sys.modules['unittest'] = FakeUnitTest
