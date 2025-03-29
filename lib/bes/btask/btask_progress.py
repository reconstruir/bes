# -*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import dataclasses
import typing

from ..system.check import check

from bes.data_classes.bdata_class_base import bdata_class_base

@dataclasses.dataclass
class btask_progress(bdata_class_base):
  value: int
  minimum: typing.Optional[int] = None
  maximum: typing.Optional[int] = None
  message: typing.Optional[str] = None

  def __post_init__(self):
    if self.maximum == None:
      if self.minimum != None:
        raise ValueError(f'"minimum" ({self.minimum}) should be None when maximum is None')
      
      if self.value not in ( 0, 1 ):
        raise ValueError(f'"value" should be either 0 or 1 when maximum is None: value="{self.value}"')
    else:
      if self.minimum == None:
        raise ValueError(f'"minimum" should be given if "maximum" ({self.maximum}) is given')

      if self.maximum < self.minimum:
        raise ValueError(f'"maximum" should be >= "minimum" : minimum="{self.minimum}" maximum="{self.maximum}"')

      if self.value < self.minimum:
        raise ValueError(f'"value" ({self.value}) should be >= "minimum" {self.minimum}')

      if self.value > self.maximum:
        raise ValueError(f'"value" ({self.value}) should be <= "maximum" {self.maximum}')

  @property
  def percent_done(self):
    if self.maximum == None:
      raise ValueError('cannot compute percent done because maximum is not given.')
    left = float(self.value - self.minimum)
    delta = float(self.maximum - self.minimum)
    return (left * 100.0) / delta
  
btask_progress.register_check_class()
