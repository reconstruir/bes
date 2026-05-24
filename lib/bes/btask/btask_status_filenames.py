# -*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import dataclasses
import typing

from ..system.check import check

from .btask_status import btask_status

@dataclasses.dataclass
class btask_status_filenames(btask_status):
  filenames: list

check.register_class(btask_status_filenames, include_seq = False)
