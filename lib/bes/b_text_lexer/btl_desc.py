#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

from ..system.check import check
from ..version.semantic_version import semantic_version

from .btl_header import btl_header
from .btl_desc_error_list import btl_desc_error_list
from .btl_desc_char_list import btl_desc_char_list

class btl_desc(namedtuple('btl_desc', 'header, tokens, errors, chars, states')):
  
  def __new__(clazz, header, tokens, errors, chars, states):
    header = check.check_btl_header(header)
    check.check_string_seq(tokens)
    errors = check.btl_desc_error_list(errors)
    chars = check.btl_desc_char_list(chars)
    return clazz.__bases__[0].__new__(clazz, header, tokens, errors, chars, states)

check.register_class(btl_desc)
