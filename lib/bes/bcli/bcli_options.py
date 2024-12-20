 #-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import copy
import pprint
 
from collections import namedtuple

from bes.system.check import check
from bes.system.log import logger

from .bcli_options_desc import bcli_options_desc

class bcli_options(object):

  _log = logger('bcli')
  
  def __init__(self, desc, **kwargs):
    desc = check.check_bcli_options_desc(desc)
    super().__setattr__('_desc', desc)
    options = {}
    super().__setattr__('_options', options)
    for name, value in kwargs.items():
      setattr(self, name, value)
    self.init_hook()

  def __str__(self):
    return self.to_str()

  def init_hook(self):
    pass

  def setattr_hook(self, name):
    pass
  
  _SECRET_OBFUSCATION_LENGTH = 13
  def to_dict(self, hide_secrets = True):
    desc = super().__getattribute__('_desc')
    d = {}
    for key in self.keys():
      value = getattr(self, key)
      if hide_secrets and desc.secret(key):
        value = '*' * self._SECRET_OBFUSCATION_LENGTH
      d[key] = value
    return copy.deepcopy(d)

  def to_str(self, hide_secrets = True):
    return pprint.pformat(self.to_dict(hide_secrets = hide_secrets))

  def keys(self):
    desc = super().__getattribute__('_desc')
    return desc.keys()

  def secret_keys(self):
    desc = super().__getattribute__('_desc')
    result = []
    return desc.keys()

  def pass_through_keys(self):
    return ()
  
  @property
  def desc(self):
    self._log.log_method_d()
    return self._desc

  def has_option(self, name):
    check.check_string(name)
    return self._desc.has_option(name)
  
  def __getattr__(self, name):
    self._log.log_method_d()
    
    if name in self.pass_through_keys():
      return super().__getattribute__(name)
    desc = super().__getattribute__('_desc')
    if not desc.has_option(name):
      raise KeyError(f'Unknown option: "{name}"')
    options = super().__getattribute__('_options')
    if name in options:
      return options[name]
    return desc.default(name)

  def __setattr__(self, name, value):
    self._log.log_method_d()
    
    if name in self.pass_through_keys():
      super().__setattr__(name, value)
      return
    desc = super().__getattribute__('_desc')
    if not desc.has_option(name):
      raise KeyError(f'Unknown option: "{name}"')
    desc_item = desc.items_dict[name]
    options = super().__getattribute__('_options')
    if value != None:
      if not desc.check_value_type(name, value, desc_item):
        type_name = desc_item.type_name
        type_item = desc._manager._types[type_name]
        value = type_item.parse(value)
      if not desc.check_value_type(name, value, desc_item):
        raise KeyError(f'Invalid type "{type(value).__name__}" for option "{name}" with value "{value}" - should be "{desc_item.option_type.__name__}"')
    options[name] = value
    self.setattr_hook(name)

  @classmethod
  def register_check_class(clazz):
    check.register_class(clazz, include_seq = False)

  def clone(self):
    d = self.to_dict(hide_secrets = False)
    return self.__class__(**d)

  def __eq__(self, other):
    check.check_bcli_options(other)

    dself = self.to_dict(hide_secrets = False)
    dother = other.to_dict(hide_secrets = False)
    return dself == dother

  @classmethod
  def clone_or_create(clazz, options, check_class_name = None):
    if not options:
      return clazz()
    if check_class_name:
      check_func = getattr(check, check_class_name)
      options = check_func(options)
    return options.clone()
  
check.register_class(bcli_options, include_seq = False)
