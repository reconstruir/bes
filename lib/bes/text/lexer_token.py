#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

class lexer_token(namedtuple('lexer_token', 'token_type, value, position')):

  def __new__(clazz, token_type = None, value = None, position = (1, 1)):
    return clazz.__bases__[0].__new__(clazz, token_type, value, position)

  def __str__(self):
    return '%s,%s,%s' % (self.token_type, self.value, self.position)
