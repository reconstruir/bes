# -*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import dataclasses
import typing

from ..system.check import check
from ..data_classes.bdata_class_base import bdata_class_base

@dataclasses.dataclass
class btask_status_base(bdata_class_base):
  task_id: int
    
check.register_class(btask_status_base, name = 'btask_status', include_seq = False)
