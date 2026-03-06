# -*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import dataclasses

from ..system.check import check

from .btask_status import btask_status
from .btask_step_progress import btask_step_progress

@dataclasses.dataclass
class btask_status_step_progress(btask_status):
  step_progress: btask_step_progress

check.register_class(btask_status_step_progress, include_seq = False)
