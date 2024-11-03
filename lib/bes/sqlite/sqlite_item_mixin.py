#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from ..system.check import check

from .sqlite_error import sqlite_error

class sqlite_item_mixin:
  'This mixing assumes that "self" is a namedtuple'

  @classmethod
  def sql_for_insert(clazz, table_name, exclude = None):
    check.check_string(table_name)
    check.check_set(exclude, entry_type = check.STRING_TYPES, allow_none = True)

    fields = clazz._resolve_fields(exclude)
    values = ', '.join('?' * len(fields))
    keys = ', '.join(fields)
    return f'insert into {table_name}({keys}) values({values})'

  @classmethod
  def sql_for_replace(clazz, table_name, exclude = None):
    check.check_string(table_name)
    check.check_set(exclude, entry_type = check.STRING_TYPES, allow_none = True)

    fields = clazz._resolve_fields(exclude)
    values = ', '.join('?' * len(fields))
    keys = ', '.join(fields)
    return f'replace into {table_name}({keys}) values({values})'

  @classmethod
  def _resolve_fields(clazz, exclude):
    if exclude == None:
      return clazz._fields
    return tuple([ field for field in clazz._fields if field not in exclude ])
  
  @classmethod
  def from_sql_row(clazz, row, error_class = None, exclude = None):
    check.check_tuple(row)
    check.check_class(error_class, allow_none = True)
    check.check_set(exclude, entry_type = check.STRING_TYPES, allow_none = True)
    
    error_class = error_class or sqlite_error

    if exclude:
      filled_row = []
      row_copy = list(row[:])
      for field in clazz._fields:
        if field in exclude:
          filled_row.append(None)
        else:
          filled_row.append(row_copy.pop(0))
    else:
      filled_row = row
    
    length = len(filled_row)
    expected_length = len(clazz._fields)
    if length != expected_length:
      raise error_class(f'Length of row should be {expected_length} instead of {length} - {row}')
    return clazz(*filled_row)
  
