#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

class variable_pattern(object):

  AT_SIGN = 1 << 0
  BRACKET = 1 << 1
  DOLLAR_ONLY = 1 << 2
  PARENTHESIS = 1 << 3
  PERCENT = 1 << 4
  PERCENT_ONLY = 1 << 5

  ALL = AT_SIGN | BRACKET | DOLLAR_ONLY | PARENTHESIS | PERCENT | PERCENT_ONLY
