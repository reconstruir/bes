#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import dataclasses
import typing

from datetime import datetime

from bes.data_classes.bdata_class_base import bdata_class_base
from bes.system.check import check

from ..bf_entry_list import bf_entry_list
from .bf_file_scanner_stats import bf_file_scanner_stats

@dataclasses.dataclass
class bf_file_scanner_result(bdata_class_base):
  entries: bf_entry_list
  stats: bf_file_scanner_stats

check.register_class(bf_file_scanner_result, include_seq = False)
