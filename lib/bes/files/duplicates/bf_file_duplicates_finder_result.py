#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import dataclasses
import typing

from bes.data_classes.bdata_class_base import bdata_class_base
from bes.system.check import check

from ..bf_entry_list import bf_entry_list
from .bf_file_duplicates_finder_item import bf_file_duplicates_finder_item

  _find_duplicates_result = namedtuple('_find_duplicates_result', 'items, resolved_files')


@dataclasses.dataclass
class bf_file_duplicates_finder_result(bdata_class_base):
  items: typing.List[bf_file_duplicates_finder_item]
  resolved_files: bf_entry_list

check.register_class(bf_file_duplicates_finder_result, include_seq = False)
