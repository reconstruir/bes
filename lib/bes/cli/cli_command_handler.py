#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import copy
from bes.cli.argparser_handler import argparser_handler
from bes.common.check import check

class cli_command_handler(object):

  def __init__(self, cli_args, options_class = None):
    check.check_dict(cli_args)
    check.check_class(options_class, allow_none = True)
    self._cli_args = cli_args
    self.options, self._args = self._make_options(options_class, cli_args)

  @classmethod
  def _make_options(clazz, options_class, cli_args):
    if not options_class:
      return None, copy.deepcopy(cli_args)
    else:
      options = options_class(**cli_args)
      args = argparser_handler.filter_keywords_args(options_class, cli_args)
      return options, args
    
  def handle_command(self, command_name):
    check.check_string(command_name)

    func = getattr(self, command_name)
    return func(**self._args)
