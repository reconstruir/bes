#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

from bes.system.check import check
from bes.common.json_util import json_util

class bf_file_resolver_result(namedtuple('bf_file_resolver_result', 'entries, stats')):

  def __new__(clazz, entries, stats):
    check.check_bf_entry_list(entries)
    check.check_bf_file_resolver_stats(stats)

    return clazz.__bases__[0].__new__(clazz, entries, stats)

  def to_dict(self):
    return dict(self._asdict())
  
  def to_json(self):
    return json_util.to_json(self.to_dict(), indent = 2, sort_keys = True)
  
check.register_class(bf_file_resolver_result, include_seq = False)
