#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system.check import check

class sqlite_item_mixin:
  'This mixing assumes that "self" is a namedtuple'

  def sql_for_insert(self, table_name):
    check.check_string(table_name)
    
    fields = self._fields
    values = ', '.join('?' * len(fields))
    keys = ', '.join(fields)
    return f'insert into {table_name}({keys}) values({values})'

  def sql_for_replace(self, table_name):
    check.check_string(table_name)

    fields = self._fields
    values = ', '.join('?' * len(fields))
    keys = ', '.join(fields)
    return f'replace into {table_name}({keys}) values({values})'

  @classmethod
  def from_sql_row(clazz, row):
    check.check_tuple(row)

    length = len(row)
    expected_length = len(clazz._fields)
    if len(row) != len(clazz._fields):
      raise vb_error('Length of row should be {expected_length} instead of {length} - {row}')
    return clazz(*row)
  
