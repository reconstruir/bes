#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import json

from collections import namedtuple

from .check import check

class shell_path_diff_result(namedtuple('shell_path_diff_result', 'appended, prepended, removed')):

  def __new__(clazz, appended, prepended, removed):
    check.check_string_seq(appended)
    check.check_string_seq(prepended)
    check.check_string_seq(removed)
    
    return clazz.__bases__[0].__new__(clazz, appended, prepended, removed)

  def to_dict(self):
    return dict(self._asdict())

  def to_json(self):
    return json.dumps(self.to_dict(), indent = 2, sort_keys = True)
  
check.register_class(shell_path_diff_result, include_seq = False)
