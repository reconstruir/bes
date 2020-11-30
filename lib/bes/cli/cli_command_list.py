#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common.check import check
from bes.common.type_checked_list import type_checked_list

from .cli_command import cli_command 

class cli_command_list(type_checked_list):

  __value_type__ = cli_command

  def __init__(self, values = None):
    super(cli_command_list, self).__init__(values = values)

  _CLASS_NAMES = set()
  def make_handler_superclass(self, class_name, extra_super_classes = None):
    'Return a class suitable for handler_object of argparser_handler.main()'

    extra_super_classes = extra_super_classes or []
    if class_name in self._CLASS_NAMES:
      raise RuntimeError('class_name already used: "{}"'.format(class_name))
    
    self._CLASS_NAMES.add(class_name)
    super_classes = [ value.cli_args_class for value in self ] + extra_super_classes
    new_class = type(class_name, tuple(super_classes), {})
    return new_class
    
check.register_class(cli_command_list, include_seq = False)
