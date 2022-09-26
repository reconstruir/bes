#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

from ..system.check import check

class text_span(namedtuple('text_span', 'start, end')):
  
  def __new__(clazz, start, end):
    check.check_int(start)
    check.check_int(end)
    
    return clazz.__bases__[0].__new__(clazz, start, end)

  def __str__(self):
    return '%s:%s' % (self.start, self.end)
  
  def __repr__(self):
    return str(self)

  
check.register_class(text_span)
