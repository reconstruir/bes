#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import dataclasses

from bes.system.check import check
from bes.btask.btask_status import btask_status

@dataclasses.dataclass
class bf_media_scan_status(btask_status):
  entries: list   # list of bf_media_file_entry
  found:   int
  scanned: int

check.register_class(bf_media_scan_status, include_seq=False)
