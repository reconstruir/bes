#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import copy
import inspect

from bes.cli.argparser_handler import argparser_handler
from ..system.check import check
from bes.common.inspect_util import inspect_util

from .bcli_missing_command_error import bcli_missing_command_error
from .bcli_options import bcli_options

class bcli_command_handler(object):

  def __init__(self, cli_args, options_class = None, delegate = None):
    check.check_dict(cli_args)
    check.check_class(options_class, allow_none = True)
    check.check_callable(delegate, allow_none = True)

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
      options = options_class()
      args = {}
      for caca_key, caca_value in cli_args.items():
        if options.has_option(caca_key):
          setattr(options, caca_key, caca_value)
        else:
          args[caca_key] = caca_value
      #args = clazz._filter_keywords_args(options_class, cli_args)
      if isinstance(options, bcli_options):
        pass
        #config_file_key = options.config_file_key()
        #if config_file_key and config_file_key in args:
        #  del args[config_file_key]
      return options, args
    
  def handle_command(self, command_name):
    if not command_name:
      raise bcli_missing_command_error('{}.handle_command() - missing command'.format(self.__class__))
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

    criteria = []
    criteria.append(bool(spec.args))
    criteria.append(len(spec.args) == 3)
    criteria.append(bool(spec.varargs))
    if hasattr(spec, 'keywords'):
      criteria.append(bool(spec.keywords))
    
    if False in criteria:
      msg = 'delegte signature should be exactly (self, command_name, options, *args, **kwargs) - {}'.format(delegate)
      raise RuntimeError(msg)

  def handle_boolean_result(self, result, verbose):
    if verbose:
      print(str(result))
    return 0 if result else 1
  
  @classmethod
  def _filter_keywords_args(clazz, options_clazz, kargs):
    check.check_class(options_clazz)

    fields = clazz._options_clazz_all_attributes(options_clazz)
    copied_args = copy.deepcopy(kargs)
    for field in fields:
      if field in copied_args:
        del copied_args[field]
    return copied_args

  
  @classmethod
  def _options_clazz_attributes(clazz, options_clazz):
    result = []
    instance = options_clazz()
    for name, _ in inspect.getmembers(instance, lambda m: not callable(m)):
      if not name.startswith('_'):
        result.append(name)
    return result
  
  @classmethod
  def _options_clazz_all_attributes(clazz, options_clazz):
    result = []
    result.extend(clazz._options_clazz_attributes(options_clazz))
    for base_clazz in options_clazz.__bases__:
      if base_clazz != bcli_options:
        result.extend(clazz._options_clazz_attributes(base_clazz))
    return result

  @property
  def blurber(self):
    blurber = getattr(self.options, 'blurber', None)
    if not blurber:
      raise RuntimeError(f'ERROR: no blurber in self.options')
    return blurber
  
  def blurb(self, *args, **kargs):
    self.blurber.blurb(*args, **kargs)

  def blurb_verbose(self, *args, **kargs):
    self.blurber.blurb_verbose(*args, **kargs)
