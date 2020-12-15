#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common.check import check
from bes.common.type_checked_list import type_checked_list

from .cli_command import cli_command 

class cli_command_list(type_checked_list):

  __value_type__ = cli_command

  def __init__(self, values = None):
    super(cli_command_list, self).__init__(values = values)

  _CLASS_NAMES = set()
  def make_handler_superclass(self, class_name):
    'Return a class suitable for handler_object of argparser_handler.main()'

    if class_name in self._CLASS_NAMES:
      raise RuntimeError('class_name already used: "{}"'.format(class_name))
    
    self._CLASS_NAMES.add(class_name)
    super_classes = [ value.cli_args_class for value in self ]
    new_class = type(class_name, tuple(super_classes), {})
    return new_class

  def duplicate_handlers(self):
    'Return a dictionary of handlers with duplicate names'

    counts = {}
    method_names = {}
    for item in self:
      class_name = item.cli_args_class.__name__
      for next_method_name in dir(item.cli_args_class):
        if next_method_name.startswith('_command'):
          if not next_method_name in method_names:
            method_names[next_method_name] = []
          method_names[next_method_name].append(( item.cli_args_class, item.filename ))

    dups = {}
    for method_name, cli_args_classes in method_names.items():
      if len(cli_args_classes) > 1:
        dups[method_name] = cli_args_classes[:]
    return dups
  
check.register_class(cli_command_list, include_seq = False)
