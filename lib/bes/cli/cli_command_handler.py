#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import copy
import inspect

from bes.cli.argparser_handler import argparser_handler
from bes.common.check import check
from bes.common.inspect_util import inspect_util

from .cli_options import cli_options

class cli_command_handler(object):

  def __init__(self, cli_args, options_class = None, delegate = None):
    check.check_dict(cli_args)
    check.check_class(options_class, allow_none = True)
    check.check_function(delegate, allow_none = True)

    if delegate:
      self._check_delegate(delegate)
    
    self._cli_args = cli_args
    self._delegate = delegate
    self.options, self._kwargs = self.make_options(options_class, cli_args)

  @classmethod
  def make_options(clazz, options_class, cli_args):
    if not options_class:
      return None, copy.deepcopy(cli_args)
    else:
      options = options_class(**cli_args)
      args = argparser_handler.filter_keywords_args(options_class, cli_args)
      if isinstance(options, cli_options):
        config_file_key = options.config_file_key()
        if config_file_key and config_file_key in args:
          del args[config_file_key]
      return options, args
    
  def handle_command(self, command_name):
    check.check_string(command_name)

    if self._delegate:
      args = ()
      result = self._delegate(command_name, self.options, *args, **self._kwargs)
    else:
      func = getattr(self, command_name)
      result = func(**self._kwargs)
    return result

  @classmethod
  def _check_delegate(clazz, delegate):
    spec = inspect_util.getargspec(delegate)
    if False in ( bool(spec.args), len(spec.args) == 3, bool(spec.varargs), bool(spec.keywords) ):
      msg = 'delegte signature should be exactly (self, command_name, options, *args, **kwargs) - {}'.format(delegate)
      raise RuntimeError(msg)
