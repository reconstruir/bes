#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import json
import dataclasses
import typing

from ..common.json_util import json_util
from ..common.time_util import time_util
from ..data_output.data_output import data_output
from ..files.bf_file_ops import bf_file_ops
from ..system.check import check
from ..text.text_replace import text_replace

class bdata_class_base(object):
  
  def to_dict(self):
    d = dataclasses.asdict(self)
    return self.to_json_dict_hook(d)

  def to_json_dict(self):
    return self.to_dict()
  
  def to_json_dict_hook(self, d):
    return d

  @classmethod
  def from_dict_hook(clazz, d):
    return d
  
  def to_json(self, replacements = None):
    d = self.to_dict()
    json_str = json_util.to_json(d, indent = 2, sort_keys = False)
    if replacements:
      json_str = text_replace.replace(json_str, replacements)
    return json_str

  def to_list(self):
    return [ getattr(self, field.name) for field in dataclasses.fields(self) ]
  
  def to_tuple(self):
    return tuple(self.to_list())
  
  def to_table(self):
    return [ ( field.name, getattr(self, field.name) ) for field in dataclasses.fields(self) ]

  def clone(self, mutations: typing.Optional[dict] = None) -> typing.Self:
    attributes = dataclasses.asdict(self)
    attributes.update(mutations or {})
    return self.__class__(**attributes)
  
  def output(self, options):
    check.check_pdb_cli_options(options)

    with bf_file_ops.open_with_default(filename = options.output_filename) as fout:
      if options.index_show_json:
        fout.write(self.to_json())
      elif options.index_brief:
        fout.write(str(self.total))
      else:
        table = self.to_table()
        data_output.output_table(table, stream = fout)

  @classmethod
  def parse_json_dict(clazz, d: dict, source: typing.Optional[str] = 'unknown') -> typing.Self:
    if not isinstance(d, dict):
      raise ValueError(f'Expected a dictionary, got {type(d)}')

    if not dataclasses.is_dataclass(clazz):
      raise TypeError(f'Class {clazz} is not a dataclass')

    hooked_d = clazz.from_dict_hook(d)
    field_names = { field.name for field in dataclasses.fields(clazz) }
    filtered_data = { key: value for key, value in hooked_d.items() if key in field_names }

    return clazz(**filtered_data)
  
  @classmethod
  def parse_json(clazz, text: str, source: typing.Optional[str] = 'unknown') -> typing.Self:
    d = json.loads(text)
    return clazz.parse_json_dict(d, source = source)

  @classmethod
  def parse_json_dict_field_enum(clazz, enum_class, d, field_name):
    value = d.get(field_name, None)
    if value == None:
      return None
    return enum_class.parse(value)

  @classmethod
  def parse_json_str_list(clazz, d, field_name):
    value = d.get(field_name, None)
    if value == None:
      return None
    result = list(d)
  
  @classmethod
  def parse_json_dict_field_date(clazz, d, field_name):
    value = d.get(field_name, None)
    if value == None:
      return None
    check.check_string(value)
    return time_util.parse_datetime_with_tz(value)
  
  def field_to_dict(self, value):
    if value == None:
      return None
    return value.to_dict()

  def field_to_str(self, value):
    if value == None:
      return None
    return str(value)

  def field_to_enum_value(self, value):
    if value == None:
      return None
    return value.value

  def field_to_str_list(self, value):
    if value == None:
      return None
    return list(value)
  
  @classmethod
  def cast_from_seq(clazz, o):
    check.check_seq(o, object)
    
    if not dataclasses.is_dataclass(clazz):
      raise TypeError(f'clazz is not a dataclass: {clazz}')
    
    fields = [ field.name for field in dataclasses.fields(clazz) ]
    values = list(o)
    num_fields = len(fields)
    num_values = len(values)
    if num_values != num_fields:
      raise ValueError(f'Length of o should be {num_fields} instead of {num_values}: {o}')
    return clazz(*values)  

  @classmethod
  def register_check_class(clazz):
    check.register_class(clazz,
                         include_seq = False,
                         cast_func = clazz.cast_from_seq)
