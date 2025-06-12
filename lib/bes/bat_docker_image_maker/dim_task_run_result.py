#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-
#

from collections import namedtuple

from ..system.check import check

class dim_task_run_result(namedtuple('dim_task_run_result', 'success, failed_entries')):

  def __new__(clazz, success, failed_entries):
    check.check_bool(success)
#    check.task_failed_entry_seq(failed_entries)
    
    return clazz.__bases__[0].__new__(clazz, success, failed_entries)
  
check.register_class(dim_task_run_result)
