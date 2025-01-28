# -*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import dataclasses
#import fields
from ..system.check import check
from .sqlite_error import sqlite_error

class sqlite_dataclass_item_mixin:
  'This mixin assumes that "self" is a dataclass'

  @classmethod
  def sql_for_insert(clazz, table_name, exclude = None):
    check.check_string(table_name)
    check.check_set(exclude, entry_type=check.STRING_TYPES, allow_none=True)

    fields = clazz._resolve_fields(exclude)
    values = ', '.join('?' * len(fields))
    keys = ', '.join(fields)
    return f'INSERT INTO {table_name}({keys}) VALUES({values})'

  @classmethod
  def sql_for_replace(clazz, table_name, exclude = None):
    check.check_string(table_name)
    check.check_set(exclude, entry_type=check.STRING_TYPES, allow_none=True)

    fields = clazz._resolve_fields(exclude)
    values = ', '.join('?' * len(fields))
    keys = ', '.join(fields)
    return f'REPLACE INTO {table_name}({keys}) VALUES({values})'

  @classmethod
  def sql_for_select_count(clazz, table_name, exclude = None):
    check.check_string(table_name)
    check.check_set(exclude, entry_type=check.STRING_TYPES, allow_none=True)

    fields = clazz._resolve_fields(exclude)
    where = ' AND '.join([ f'{field}=?' for field in fields ])
    return f'SELECT COUNT(*) FROM {table_name} WHERE({where})'

  @classmethod
  def sql_for_select(clazz, table_name, exclude = None):
    check.check_string(table_name)
    check.check_set(exclude, entry_type=check.STRING_TYPES, allow_none=True)

    fields = clazz._resolve_fields(exclude)
    selection = ', '.join(fields)
    return f'SELECT {selection} FROM {table_name}'
  
  @classmethod
  def _resolve_fields(clazz, exclude):
    if not dataclasses.is_dataclass(clazz):
      raise TypeError(f'{clazz} is not a dataclass')

    fields = [f.name for f in dataclasses.fields(clazz)]
    if exclude is None:
      return fields
    return [field for field in fields if field not in exclude]

  @classmethod
  def from_sql_row(clazz, row, error_class=None, exclude = None):
    check.check_tuple(row)
    check.check_class(error_class, allow_none=True)
    check.check_set(exclude, entry_type=check.STRING_TYPES, allow_none=True)
    
    error_class = error_class or sqlite_error

    fields = [f.name for f in dataclasses.fields(clazz)]

    if exclude:
      filled_row = []
      row_copy = list(row[:])
      for field in fields:
        if field in exclude:
          filled_row.append(None)
        else:
          filled_row.append(row_copy.pop(0))
    else:
      filled_row = row

    length = len(filled_row)
    expected_length = len(fields)
    if length != expected_length:
      raise error_class(f'Length of row should be {expected_length} instead of {length} - {row}')
    return clazz(*filled_row)
