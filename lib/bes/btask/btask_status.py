# -*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import dataclasses
import typing

from ..system.check import check

from bes.data_classes.bdata_class_base import bdata_class_base

@dataclasses.dataclass
class btask_status(bdata_class_base):
  pass
  
btask_status.register_check_class()
