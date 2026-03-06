# -*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import dataclasses
import typing

from ..system.check import check
from ..data_classes.bdata_class_base import bdata_class_base

@dataclasses.dataclass
class btask_step_progress(bdata_class_base):
  step: int
  total_steps: typing.Optional[int]
  step_title: str
  step_percent: typing.Optional[int] = None

  def __post_init__(self):
    if self.step < 0:
      raise ValueError(f'"step" must be >= 0: step="{self.step}"')
    if self.total_steps is not None and self.total_steps < 1:
      raise ValueError(f'"total_steps" must be >= 1 when given: total_steps="{self.total_steps}"')
    if self.step_percent is not None:
      if self.step_percent < 0 or self.step_percent > 100:
        raise ValueError(f'"step_percent" must be 0-100 when given: step_percent="{self.step_percent}"')

btask_step_progress.register_check_class()
