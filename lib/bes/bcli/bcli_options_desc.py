 #-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import copy
 
from collections import namedtuple
from bes.system.check import check

from .bcli_option_desc_item_list import bcli_option_desc_item_list
from .bcli_simple_type_item_list import bcli_simple_type_item_list
from .bcli_simple_type_manager import bcli_simple_type_manager

class bcli_options_desc(object):

  def __init__(self, name, types, items_desc, variables):
    check.check_string(name)
    types = check.check_bcli_simple_type_item_list(types, allow_none = True)
    check.check_string(items_desc, allow_none = True)
    check.check_dict(variables, key_type = str)

    self._name = name
    self._types = types[:]
    self._items_desc = items_desc
    self._variables = copy.deepcopy(variables)
    self._manager = bcli_simple_type_manager()
    self._manager.add_types(self._types)
    self._manager.add_variables(self._variables)
    self._items = bcli_option_desc_item_list.parse_text(self._manager, self._items_desc).to_dict()
    print(self._items)
    
check.register_class(bcli_options_desc, include_seq = False)
