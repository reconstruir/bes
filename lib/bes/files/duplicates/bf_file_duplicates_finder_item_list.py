#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system.check import check
from bes.common.json_util import json_util

from bes.data_classes.bdata_class_list_base import bdata_class_list_base

from .bf_file_duplicates_finder_item import bf_file_duplicates_finder_item

class bf_file_duplicates_finder_item_list(bdata_class_list_base):

  __value_type__ = bf_file_duplicates_finder_item

  def to_dict_list(self, replacements = None, xp_filenames = False):
    return [ item.to_dict(replacements = replacements, xp_filenames = xp_filenames) for item in self ]

  def to_json(self, replacements = None, xp_filenames = False):
    dl = self.to_dict_list(replacements = replacements, xp_filenames = xp_filenames)
    return json_util.to_json(dl)
  
bf_file_duplicates_finder_item_list.register_check_class()
