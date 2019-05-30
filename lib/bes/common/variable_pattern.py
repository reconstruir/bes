#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

class variable_pattern(object):

  DOLLAR_ONLY = 0x01
  PARENTHESIS = 0x02
  BRACKET = 0x04
  AT_SIGN = 0x08
  ALL = DOLLAR_ONLY | PARENTHESIS | BRACKET | AT_SIGN
