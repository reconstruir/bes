#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

from ..common.tuple_util import tuple_util
from ..system.check import check
    
class btl_document_insertion(namedtuple('btl_document_insertion', 'index, left_line_break, right_line_break')):

  def __new__(clazz, index, left_line_break, right_line_break):
    check.check_int(index)
    check.check_bool(left_line_break)
    check.check_bool(right_line_break)
    
    return clazz.__bases__[0].__new__(clazz, index, left_line_break, right_line_break)

check.register_class(btl_document_insertion) #, cast_func = btl_document_insertion._check_cast_func)
