#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

from bes.common.check import check

class refactor_item(namedtuple('refactor_item', 'src, dst')):

  def __new__(clazz, src, dst):
    check.check_string(src)
    check.check_string(dst)
    
    return clazz.__bases__[0].__new__(clazz, src, dst)

  def __str__(self):
    return '{}:{}'.format(self.algorithm, self.refactor_item)

  def __repr__(self):
    return str(self)

check.register_class(refactor_item, include_seq = False)
