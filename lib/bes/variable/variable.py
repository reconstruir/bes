#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import re
from string import Template

from bes.common.check import check

class variable(object):
  'Class to find an substitute shell style variabels in the forms $foo and ${foo}'
  
  @classmethod
  def substitute(clazz, s, d):
    'Substitute vars in s with d.'
    check.check_dict(d, key_type = check.STRING_TYPES, value_type = check.STRING_TYPES)
    old_result = s
    new_result = None
    while True:
      new_result = Template(old_result).safe_substitute(**d)
      if new_result == old_result:
        break
      old_result = new_result
    return new_result
  
  @classmethod
  def has_rogue_dollar_signs(clazz, s):
    'Return True of the string has rogue unescaped dollar signs.'
    s = s.replace('\\$', '')
    return '$' in s
