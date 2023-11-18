#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import json

from bes.common.json_util import json_util
from bes.common.type_checked_list import type_checked_list
from bes.system.check import check

from .mmd_transition import mmd_transition

class mmd_transition_list(type_checked_list):

  __value_type__ = mmd_transition

  def __init__(self, values = None):
    super().__init__(values = values)

  def to_dict_list(self):
    return [ item.to_dict() for item in self ]

  def to_json(self):
    d = [ item.to_dict() for item in self ]
    return json_util.to_json(d,
                             indent = 2,
                             sort_keys = False,
                             ensure_last_line_sep = True)
  
check.register_class(mmd_transition_list, include_seq = False)
