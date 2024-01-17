#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

from ..common.tuple_util import tuple_util
from ..system.check import check

from .btl_lexer_token_deque import btl_lexer_token_deque

class bkv_key(namedtuple('bkv_key', 'key, tokens')):

  def __new__(clazz, key, tokens):
    check.check_string(key)
    tokens = check.check.btl_lexer_token_deque(tokens)
    
    return clazz.__bases__[0].__new__(clazz, key, tokens)

  def __str__(self):
    return self.key

  @classmethod
  def _check_cast_func(clazz, obj):
    if check.is_tuple(obj):
      return tuple_util.cast_seq_to_namedtuple(clazz, obj)
    return obj
  
check.register_class(bkv_key, include_seq = False, cast_func = bkv_key._check_cast_func)
