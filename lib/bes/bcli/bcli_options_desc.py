#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple
from bes.system.check import check

from .bcli_option_desc_item_list import bcli_option_desc_item_list

class bcli_options_desc(namedtuple('bcli_options_desc', 'items, defaults')):

  def __new__(clazz, name, items, defaults):
    items = check.check_bcli_option_desc_item_list(items)
    check.check_dict(defaults)
    
    return clazz.__bases__[0].__new__(clazz, items, defaults)

check.register_class(bcli_options_desc, include_seq = False)
