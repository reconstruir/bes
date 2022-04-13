#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import re

from ..system.check import check

class refactor_python(object):

  _HEAD_EXPRESSION = re.compile(r'def\s+[a-zA-Z_]\w*\s*\(', re.DOTALL)
  _TAIL_EXPRESSION = re.compile(r'\)\s*\:', re.DOTALL)
  @classmethod
  def function_definition(clazz, body):
    check.check_string(body)
    
    head_match = clazz._HEAD_EXPRESSION.search(body)
    if not head_match:
      return None
    head_start, head_end = head_match.span()
    tail_match = clazz._TAIL_EXPRESSION.search(body, pos = head_end + 1)
    if not tail_match:
      return None
    tail_start, tail_end = tail_match.span()
    return body[head_start : tail_end - 1]
