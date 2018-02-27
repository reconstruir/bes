#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple
from bes.common import check

class unit_test_description(namedtuple('unit_test_description', 'filename,fixture,function')):

  def __new__(clazz, filename, fixture, function):
    if filename is not None:
      check.check_string(filename)
    if fixture is not None:
      check.check_string(fixture)
    if function is not None:
      check.check_string(function)
    return clazz.__bases__[0].__new__(clazz, filename, fixture, function)

  @classmethod
  def parse(clazz, s):
    'Parse a unit test description in the form filename:fixutre.function'
    filename, _, right = s.partition(':')
    if '.' in right:
      fixture, _, function = right.partition('.')
    else:
      fixture, function = ( None, right )
    return clazz(filename or None, fixture or None, function or None)

  def __str__(self):
    v = []
    if self.filename:
      v.append(self.filename)
      v.append('.')
    if self.fixture:
      v.append(self.fixture)
    v.append(':')
    if self.function:
      v.append(self.function)
    return ''.join(v)

check.register_class(unit_test_description)
