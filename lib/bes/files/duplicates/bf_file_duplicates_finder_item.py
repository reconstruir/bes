#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import dataclasses
import typing

from bes.data_classes.bdata_class_base import bdata_class_base
from bes.system.check import check

from ..bf_entry import bf_entry
from ..bf_entry_list import bf_entry_list

@dataclasses.dataclass
class bf_file_duplicates_finder_item(bdata_class_base):
  entry: bf_entry
  duplicates: typing.Optional[bf_entry_list]

check.register_class(bf_file_duplicates_finder_item, include_seq = False)
