#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import dataclasses
import typing

from bes.data_classes.bdata_class_base import bdata_class_base
from bes.system.check import check

from ..bf_entry import bf_entry
from ..bf_entry_list import bf_entry_list

@dataclasses.dataclass
class bf_file_dups_finder_item(bdata_class_base):
  entry: bf_entry
  duplicates: typing.Optional[bf_entry_list]

  def to_json_dict_hook(self, d):
    return {
      'entry': self.entry.to_dict(),
      'duplicates': self.duplicates.to_dict_list()if self.duplicates else [],
    }
  
check.register_class(bf_file_dups_finder_item, include_seq = False)
