#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-
#

from collections import namedtuple

from ..system.check import check

class dim_task_failed_entry(namedtuple('dim_task_failed_entry', 'descriptor, log')):

  def __new__(clazz, descriptor, log):
    check.check_dim_task_descriptor(descriptor)
    check.check_string(log)
    
    return clazz.__bases__[0].__new__(clazz, descriptor, log)
  
check.register_class(dim_task_failed_entry)
