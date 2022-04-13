#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple
import inspect

from ..system.check import check

class cli_command(namedtuple('cli_command', 'name, add_args_function, description, cli_args_class, filename')):

  def __new__(clazz, name, add_args_function, description, cli_args_class):
    filename = inspect.getfile(cli_args_class)
    return clazz.__bases__[0].__new__(clazz, name, add_args_function, description, cli_args_class, filename)

check.register_class(cli_command, include_seq = False)
