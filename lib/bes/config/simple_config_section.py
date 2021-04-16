#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os
import os.path as path
import fnmatch

from bes.common.algorithm import algorithm
from bes.common.bool_util import bool_util
from bes.common.check import check
from bes.common.list_util import list_util
from bes.common.string_util import string_util
from bes.common.tuple_util import tuple_util
from bes.common.variable import variable
from bes.compat.StringIO import StringIO
from bes.key_value.key_value import key_value
from bes.key_value.key_value_list import key_value_list
from bes.system.env_var import os_env_var

from collections import namedtuple

from .simple_config_entry import simple_config_entry
from .simple_config_error import simple_config_error
from .simple_config_origin import simple_config_origin
from .simple_config_section_header import simple_config_section_header
from .simple_config_variables import simple_config_variables

class simple_config_section(namedtuple('simple_config_section', 'header_, entries_, origin_, extends_section_, variables_, parent_variables_')):

  def __new__(clazz, header_, entries_, origin_, extends_section_ = None, parent_variables_ = None):
    check.check_simple_config_section_header(header_)
    check.check_simple_config_entry_seq(entries_, allow_none = True)
    check.check_simple_config_origin(origin_, allow_none = True)
    check.check_simple_config_section(extends_section_, allow_none = True)
    check.check_simple_config_variables(parent_variables_, allow_none = True)
    
    return clazz.__bases__[0].__new__(clazz,
                                      header_,
                                      entries_ or [],
                                      origin_,
                                      extends_section_,
                                      simple_config_variables(),
                                      parent_variables_ or simple_config_variables())

  def __iter__(self):
    return iter(self.entries_)
  
  def __str__(self):
    return self.to_string()

  def to_string(self, entry_formatter = None, sort = False, fixed_key_column_width = False):
    entry_formatter = entry_formatter or self.default_entry_formatter
    buf = StringIO()
    buf.write(str(self.header_))
    buf.write('\n')
    entries = self.entries_ if not sort else sorted(self.entries_)
    key_column_width = 0
    if fixed_key_column_width:
      for entry in entries:
        this_len = len(entry.value.key)
        if this_len > key_column_width:
          key_column_width = this_len
    for i, entry in enumerate(entries):
      if i != 0:
        buf.write('\n')
      buf.write('  ')
      buf.write(entry_formatter(entry, key_column_width = key_column_width))
    buf.write('\n')
    return buf.getvalue()

  @classmethod
  def default_entry_formatter(clazz, entry, sort = False, key_column_width = 0):
    return entry.to_string(sort = sort, key_column_width = key_column_width)

  def __getattr__(self, key):
    return self.find_by_key(key)
  
  def __setattr__(self, key, value):
    self.set_value(key, value)

  def clone(self, mutations = None):
    return tuple_util.clone(self, mutations = mutations)
  
  def find_by_key(self, key, raise_error = True, resolve_env_vars = True):
    entry = self.find_entry(key)
    if not entry and self.extends_section_:
      entry = self.extends_section_.find_entry(key)
    if not entry:
      if raise_error:
        raise simple_config_error('"{}" entry not found'.format(key), self.origin_)
      return None
    value = entry.value.value
    if resolve_env_vars:
     value = self._resolve_variables(value, entry.origin)
    return value

  def find_entry(self, key):
    index = self.entry_index(key)
    if index < 0:
      return None
    return self.entries_[index]

  def entry_index(self, key):
    for i, entry in list_util.reversed_enumerate(self.entries_):
      if entry.value.key == key:
        return i
    return -1

  def match_by_key(self, pattern, raise_error = True, resolve_env_vars = True):
    entry = self.match_entry(pattern)
    if not entry and self.extends_section_:
      entry = self.extends_section_.match_entry(pattern)
    if not entry:
      if raise_error:
        raise simple_config_error('"{}" entry not found'.format(pattern), self.origin_)
      return None
    value = entry.value.value
    if resolve_env_vars:
     value = self._resolve_variables(value, entry.origin)
    return value
  
  def match_entry(self, pattern):
    for i, entry in list_util.reversed_enumerate(self.entries_):
      if fnmatch.fnmatch(entry.value.key, pattern):
        return entry
    return None
  
  def has_key(self, key):
    return self.find_by_key(key, raise_error = False, resolve_env_vars = False) is not None

  def get_value(self, key):
    return self.find_by_key(key, raise_error = True, resolve_env_vars = True)

  def get_value_origin(self, key):
    entry = self.find_entry(key)
    if not entry:
      return None
    return entry.origin

  def get_string_list(self, key):
    return string_util.split_by_white_space(self.get_value(key), strip = True)

  def set_value(self, key, value, hints = None):
    check.check_string(key)
    check.check_string(value)
    check.check_dict(hints, allow_none = True)

    found = False
    for i, entry in enumerate(self.entries_):
      if entry.value.key == key:
        found = True
        self.entries_[i] = simple_config_entry(key_value(entry.value.key, value),
                                               origin = entry.origin,
                                               annotations = entry.annotations,
                                               hints = entry.hints)

    if found:
      return
    
    self.add_value(key, value, hints = hints)

  def add_value(self, key, value, hints = None):
    check.check_string(key)
    check.check_string(value)
    check.check_dict(hints, allow_none = True)

    if self.entries_:
      last_origin = self.entries_[-1].origin
    else:
      last_origin = self.origin_
    if last_origin:
      new_origin = simple_config_origin(last_origin.source, last_origin.line_number + 1)
    else:
      new_origin = None
    new_entry = simple_config_entry(key_value(key, value), origin = new_origin, hints = hints)
    self.entries_.append(new_entry)

  def delete_value(self, key):
    check.check_string(key)

    index = self.entry_index(key)
    if index < 0:
      return
    del self.entries_[index]

  def get_bool(self, key, default = False):
    value = self.find_by_key(key, raise_error = False, resolve_env_vars = False)
    if value is not None:
      return bool_util.parse_bool(value)
    else:
      return default
    
  def to_key_value_list(self, resolve_env_vars = False):
    'Return values as a key_value_list optionally resolving environment variables.'
    result = key_value_list()
    if self.extends_section_:
      result.extend(self.extends_section_.to_key_value_list(resolve_env_vars = resolve_env_vars))
    for entry in self.entries_:
      value = entry.value.value
      if resolve_env_vars:
        value = self._resolve_variables(value, entry.origin)
      result.append(key_value(entry.value.key, value))
    return result
  
  def to_dict(self, resolve_env_vars = True):
    'Return values as a dict optionally resolving environment variables.'
    result = {}
    if self.extends_section_:
      result.update(self.extends_section_.to_dict(resolve_env_vars = resolve_env_vars))
    for entry in self:
      if resolve_env_vars:
        value = self._resolve_variables(entry.value.value, entry.origin)
      else:
        value = entry.value.value
      result[entry.value.key] = value
    return result

  def get_all_values(self, key, resolve_env_vars = True):
    'Return all values that have key.'
    kvl = self.to_key_value_list(resolve_env_vars = resolve_env_vars)
    return [ kv.value for kv in kvl if kv.key == key ]
  
  def set_values(self, values, hints = None):
    check.check_dict(hints, allow_none = True)

    if check.is_string(values):
      kv_values = key_value_list.parse(values)
    elif check.is_key_value_list(values):
      kv_values = values
    elif check.is_dict(values):
      kv_values = key_value_list.from_dict(values)
    else:
      raise TypeError('Unknown type for values: "{}" - "{}"'.format(type(values), values))
    
    for kv in kv_values:
      self.set_value(kv.key, kv.value, hints = hints)

  def clear_values(self):
    while len(self.entries_):
      self.entries_.pop()

  def _resolve_variables(self, value, origin):
    variables = variable.find_variables(value)
    if variables:
      substitutions = self._substitutions_for_value(value, variables, origin)
      return variable.substitute(value, substitutions)
    return value
  
  def _substitutions_for_value(self, v, variables, origin):
    result = {}
    for var in variables:
      os_var = os_env_var(var)
      found = False
      if os_var.is_set:
        value = os_var.value
        found = True
      else:
        if var in self.variables_:
          value = self.variables_[var]
          found = True
        elif var in self.parent_variables_:
          value = self.parent_variables_[var]
          found = True
      if not found:  
        raise simple_config_error('Not set in the current environment: "{}"'.format(v), origin)
      result[var] = value
    return result

  def set_variable(self, key, value):
    check.check_string(key)
    check.check_value(value)

    self.variables_.set_variable(key, value)

  def set_variables(self, variables):
    check.check_dict(variables, check.STRING_TYPES, check.STRING_TYPES)

    self.variables_.set_variables(variables)

  def update_variables(self, variables):
    check.check_dict(variables, check.STRING_TYPES, check.STRING_TYPES)

    self.variables_.update_variables(variables)
    
  def variables(self):
    return self.variables_.variables()
  
check.register_class(simple_config_section)
