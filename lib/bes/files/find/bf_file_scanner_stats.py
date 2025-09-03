#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-
import dataclasses
import typing

from datetime import datetime

from bes.system.check import check
from bes.data_output.data_output import data_output
from bes.files.bf_file_ops import bf_file_ops
from bes.common.json_util import json_util

from bes.data_classes.bdata_class_base import bdata_class_base

@dataclasses.dataclass
class bf_file_scanner_stats(bdata_class_base):
  num_checked: int
  num_files_checked: int
  num_dirs_checked: int
  start_time: datetime
  end_time: datetime
  depth: int

  @property
  def duration(self):
    return self.end_time - self.start_time
  
check.register_class(bf_file_scanner_stats, include_seq = False)
