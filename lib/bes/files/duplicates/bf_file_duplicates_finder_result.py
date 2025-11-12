#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import dataclasses
import typing

from bes.data_classes.bdata_class_base import bdata_class_base
from bes.system.check import check

from ..bf_entry_list import bf_entry_list
from .bf_file_duplicates_finder_item import bf_file_duplicates_finder_item
from .bf_file_duplicates_finder_item_list import bf_file_duplicates_finder_item_list

@dataclasses.dataclass
class bf_file_duplicates_finder_result(bdata_class_base):
  resolved_entries: bf_entry_list
  duplicate_items: bf_file_duplicates_finder_item_list

  def to_dict(self, replacements = None, xp_filenames = False):
    return {
      'resolved_entries': self.resolved_entries.to_dict_list(replacements = replacements, xp_filenames = xp_filenames),
      'duplicate_items': self.duplicate_items.to_dict_list(replacements = replacements, xp_filenames = xp_filenames),
    }

  def to_json(self, replacements = None, xp_filenames = False):
    d = self.to_dict(replacements = replacements, xp_filenames = xp_filenames)
    return json_util.to_json(dl, indent = 2, sort_keys = True)

check.register_class(bf_file_duplicates_finder_result, include_seq = False)
