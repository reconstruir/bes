#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import dataclasses
import typing

from bes.data_classes.bdata_class_base import bdata_class_base
from bes.system.check import check

from .bf_file_finder_progress_state import bf_file_finder_progress_state
from .bf_file_finder_error import bf_file_finder_error

@dataclasses.dataclass
class bf_file_finder_progress(bdata_class_base):
  state: typing.Union[bf_file_finder_progress_state, str]
  index: typing.Optional[int] = None
  total: typing.Optional[int] = None

  def __post_init__(self):
    self.state = check.check_bf_file_finder_progress_state(self.state)

  def to_json_dict_hook(self, d):
    d['state'] = self.field_to_enum_value(self.state)
    return d
    
  @property
  def rounded_percent_done(self):
    return round(self.percent_done)

  @property
  def percent_done(self):
    return (self.index / self.total) * 100.0
  
check.register_class(bf_file_finder_progress, include_seq = False)
