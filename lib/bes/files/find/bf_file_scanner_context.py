#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import dataclasses

from datetime import datetime

from bes.data_classes.bdata_class_base import bdata_class_base
from bes.system.check import check

from .bf_file_scanner_stats import bf_file_scanner_stats

@dataclasses.dataclass
class bf_file_scanner_context(bdata_class_base):
  stats: dict
  ignore_files: dict  

  def __init__(self):
    self.stats = {
      'num_checked': 0,
      'num_files_checked': 0,
      'num_dirs_checked': 0,
      'start_time': datetime.now(),
      'end_time': None,
      'depth': 0,
    }
    self.ignore_files_dict = {}

  def make_stats(self):
    return bf_file_scanner_stats(self.stats['num_checked'],
                                 self.stats['num_files_checked'],
                                 self.stats['num_dirs_checked'],
                                 self.stats['start_time'],
                                 datetime.now(),
                                 self.stats['depth'])
    
check.register_class(bf_file_scanner_context, include_seq = False)
