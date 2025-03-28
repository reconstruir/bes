# -*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from ..system.check import check

class btask_status_base(bdata_class_base):

  def __init__(self, task_id, status_type):
    check.check_int(task_id)
    check.check_string(status_type)

    self.task_id = task_id
    self.status_type = status_type
    
check.register_class(btask_status_base, name = 'btask_status', include_seq = False)
