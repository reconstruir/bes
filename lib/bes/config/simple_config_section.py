#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common.bool_util import bool_util
from bes.common.check import check
from bes.common.variable import variable
from bes.compat.StringIO import StringIO
from bes.key_value.key_value import key_value
from bes.key_value.key_value_list import key_value_list
from bes.system.env_var import os_env_var

from collections import namedtuple

from .simple_config_error import simple_config_error
from .simple_config_origin import simple_config_origin
from .simple_config_entry import simple_config_entry
from .simple_config_section_header import simple_config_section_header

class simple_config_section(namedtuple('simple_config_section', 'header, entries, origin')):

  def __new__(clazz, header, entries, origin):
    check.check_simple_config_section_header(header)
    check.check_simple_config_entry_seq(entries, allow_none = True)
    check.check_simple_config_origin(origin, allow_none = True)
    
    return clazz.__bases__[0].__new__(clazz, header, entries or [], origin)

  @property
  def name(self):
    return self.header.name
  
  def __str__(self):
    buf = StringIO()
    buf.write(self.name)
    buf.write('\n')
    for i, entry in enumerate(self.entries):
      if i != 0:
        buf.write('\n')
      buf.write('  ')
      buf.write(str(entry))
    return buf.getvalue()

#  def __getitem__(self, key):
#    return self.find_by_key(key)

#  def __setitem__(self, key, value):
#    self.set_value(key, value)
  
  def find_by_key(self, key, raise_error = True, resolve_env_vars = True):
    entry = self.find_entry(key)
    if not entry:
      if raise_error:
        raise simple_config_error('"{}" entry not found'.format(key), self.origin)
      return None
    value = entry.value.value
    if resolve_env_vars:
     value = self._resolve_variables(value, entry.origin)
    return value

  def find_entry(self, key):
    index = self.entry_index(key)
    if index < 0:
      return None
    return self.entries[index]

  def entry_index(self, key):
    for i, entry in enumerate(self.entries):
      if entry.value.key == key:
        return i
    return -1

  def has_key(self, key):
    return self.find_entry(key) is not None

  def get_value(self, key):
    return self.find_by_key(key, raise_error = True, resolve_env_vars = True)

  def set_value(self, key, value):
    check.check_string(key)
    check.check_string(value)

    index = self.entry_index(key)
    if index >= 0:
      entry = self.entries[index]
      assert entry.value.key == key
      self.entries[index] = simple_config_entry(key_value(entry.value.key, value), entry.origin, entry.annotations)
      return
    
    if self.entries:
      last_origin = self.entries[-1].origin
    else:
      last_origin = self.origin
    if last_origin:
      new_origin = simple_config_origin(last_origin.source, last_origin.line_number + 1)
    else:
      new_origin = None
    new_entry = simple_config_entry(key_value(key, value), origin = new_origin)
    self.entries.append(new_entry)
    
  def get_bool(self, key, default = False):
    value = self.find_by_key(key, raise_error = False, resolve_env_vars = False)
    if value is not None:
      return bool_util.parse_bool(value)
    else:
      return default
    
  def to_key_value_list(self, resolve_env_vars = False):
    'Return values as a key_value_list optionally resolving environment variables.'
    result = key_value_list()
    for entry in self.entries:
      value = entry.value.value
      if resolve_env_vars:
        value = self._resolve_variables(value, entry.origin)
      result.append(key_value(entry.value.key, value))
    return result
  
  def to_dict(self, resolve_env_vars = True):
    'Return values as a dict optionally resolving environment variables.'
    return self.to_key_value_list(resolve_env_vars = resolve_env_vars).to_dict()

  def set_values(self, values):
    if isinstance(values, key_value_list):
      values = key_value_list.to_dict()
    elif isinstance(values, dict):
      pass
    else:
      raise TypeError('values should be of type dict or key_value_list: {}'.format(type(values)))
    for key, value in values.items():
      self.set_value(key, value)
  
  @classmethod
  def _resolve_variables(clazz, value, origin):
    variables = variable.find_variables(value)
    if variables:
      substitutions = clazz._substitutions_for_value(value, origin)
      return variable.substitute(value, substitutions)
    return value
  
  @classmethod
  def _substitutions_for_value(clazz, v, origin):
    result = {}
    variables = variable.find_variables(v)
    for var in variables:
      os_var = os_env_var(var)
      if not os_var.is_set:
        raise simple_config_error('Not set in the current environment: %s' % (v), origin)
      result[var] = os_var.value
    return result
  
check.register_class(simple_config_section)
