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
