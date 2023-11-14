#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

from ..common.string_util import string_util
from ..common.tuple_util import tuple_util
from ..system.check import check

class mmd_document(namedtuple('mmd_document', 'states, tokens')):

  def __new__(clazz, states, tokens):
    check.check_string_seq(states)
    check.check_string_seq(tokens)

    return clazz.__bases__[0].__new__(clazz, states, tokens)

check.register_class(mmd_document, include_seq = False)
