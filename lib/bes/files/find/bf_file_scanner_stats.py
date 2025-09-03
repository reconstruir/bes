#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

from bes.system.check import check
from bes.common.json_util import json_util

class bf_file_scanner_stats(namedtuple('bf_file_scanner_stats', 'num_checked, num_files_checked, num_dirs_checked, start_time, end_time, depth')):

  def __new__(clazz, num_checked, num_files_checked, num_dirs_checked, start_time, end_time, depth):
    check.check_int(num_checked)
    check.check_int(num_files_checked)
    check.check_datetime(start_time)
    check.check_datetime(end_time)
    check.check_int(depth)
    
    return clazz.__bases__[0].__new__(clazz, num_checked, num_files_checked, num_dirs_checked, start_time, end_time, depth)

  def to_dict(self):
    return dict(self._asdict())
  
  def to_json(self):
    return json_util.to_json(self.to_dict(), indent = 2, sort_keys = True)
  
  @property
  def duration(self):
    return self.end_time - self.start_time

check.register_class(bf_file_scanner_stats, include_seq = False)
