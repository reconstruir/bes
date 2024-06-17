 #-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple
from bes.system.check import check
from bes.system.log import logger

from .bcli_options_desc import bcli_options_desc

class bcli_options(object):

  _log = logger('bcli_options')
  
  def __init__(self, desc, **kwargs):
    desc = check.check_bcli_options_desc(desc)
    super().__setattr__('_desc', desc)
    options = {}
    super().__setattr__('_options', options)
    for name, value in kwargs.items():
      setattr(self, name, value)

  @property
  def desc(self):
    self._log.log_method_d()
    return self._desc

  def has_option(self, name):
    check.check_string(name)
    return self._desc.has_option(name)
  
  def __getattr__(self, name):
    self._log.log_method_d()
    desc = super().__getattribute__('_desc')
    if not desc.has_option(name):
      raise KeyError(f'Unknown option: "{name}"')
    options = super().__getattribute__('_options')
    if name in options:
      return options[name]
    return desc.default_value(name)

  def __setattr__(self, name, value):
    self._log.log_method_d()
    desc = super().__getattribute__('_desc')
    if not desc.has_option(name):
      raise KeyError(f'Unknown option: "{name}"')
    desc_item = desc.items_dict[name]
    options = super().__getattribute__('_options')
    if not desc.check_value_type(name, value):
      raise KeyError(f'Invalid type {type(value).__name__} for "{name}" ({value}) - should be "{desc_item.option_type.__name__}"')
    options[name] = value

check.register_class(bcli_options, include_seq = False)
