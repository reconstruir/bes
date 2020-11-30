#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common.check import check
from bes.common.type_checked_list import type_checked_list

from .cli_item import cli_item 

class cli_item_list(type_checked_list):

  __value_type__ = cli_item

  def __init__(self, values = None):
    super(cli_item_list, self).__init__(values = values)

  _CLASS_NAMES = set()
  def make_handler_superclass(self, class_name):
    'Return a class suitable for handler_object of argparser_handler.main()'

    if class_name in self._CLASS_NAMES:
      raise RuntimeError('class_name already used: "{}"'.format(class_name))
    
    self._CLASS_NAMES.add(class_name)
    super_classes = [ value.cli_args_class for value in self ] + [ object ]
    new_class = type(class_name, tuple(super_classes), {})
    return new_class
    
check.register_class(cli_item_list, include_seq = False)
