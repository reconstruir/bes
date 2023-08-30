# -*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

from ..system.check import check

class btask_initializer(namedtuple('btask_initializer', 'function, args')):
  
  def __new__(clazz, function, args):
    check.check_callable(function, allow_none = True)
    check.check_tuple(args, allow_none = True)

    return clazz.__bases__[0].__new__(clazz, function, args)

  def call(self):
    if not self.function:
      return False
    args = self.args or ()
    self.function(*args)
  
check.register_class(btask_initializer, include_seq = False)
  
