# -*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import dataclasses
import typing

from ..system.check import check
from ..data_classes.bdata_class_base import bdata_class_base

from .btask_status_base import btask_status_base
@dataclasses.dataclass
class _btask_status_queue_item(bdata_class_base):
  task_id: int
  status: btask_status_base
    
check.register_class(_btask_status_queue_item, include_seq = False)
