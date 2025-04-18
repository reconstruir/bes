# -*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import dataclasses

from ..system.check import check

from .btask_progress import btask_progress
from .btask_status import btask_status

@dataclasses.dataclass
class btask_status_progress(btask_status):
  progress: btask_progress
  
check.register_class(btask_status_progress, include_seq = False)
