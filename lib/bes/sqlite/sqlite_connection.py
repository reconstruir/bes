#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import sqlite3

from datetime import datetime
from datetime import timezone

from ..system.log import logger
from ..system.check import check

class sqlite_connection(sqlite3.Connection):

  _log = logger('bsqlite')
  
  _adapters_registered = False

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    if not self._adapters_registered:
      self._register_custom_adapters_and_converters()
      self._adapters_registered = True

  @classmethod
  def _register_custom_adapters_and_converters(clazz):
    sqlite3.register_adapter(datetime, clazz._timestamp_adapt)
    sqlite3.register_converter('timestamp', clazz._timestamp_convert)

  @classmethod
  def _timestamp_adapt(clazz, ts_date):
    check.check_datetime(ts_date)

    if ts_date.tzinfo is None:
      ts_str = ts_date.strftime('%Y-%m-%d %H:%M:%S')
    else:
      ts_str = ts_date.astimezone(timezone.utc).strftime('%Y-%m-%d %H:%M:%S%z')
    clazz._log.log_d(f'_timestamp_adapt: ts_date={ts_date} ts_date.tzinfo={ts_date.tzinfo} ts_str={ts_str}')
    return ts_str

  @classmethod
  def _timestamp_convert(clazz, ts_bytes):
    check.check_bytes(ts_bytes)

    ts_str = ts_bytes.decode('utf-8')
    clazz._log.log_d(f'_timestamp_convert: ts_str={ts_str}')
    if '+' in ts_str:
      tz_format = '%Y-%m-%d %H:%M:%S%z'
    else:
      tz_format = '%Y-%m-%d %H:%M:%S'
    date = datetime.strptime(ts_str, tz_format)
    return date
