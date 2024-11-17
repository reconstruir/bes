#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import sqlite3

from datetime import datetime
from datetime import timezone

from ..system.log import logger
from ..system.check import check
from ..common.time_util import time_util

class sqlite_datetime_adapter_converter(object):

  _log = logger('bsqlite')
  
  _adapters_registered = False

  @classmethod
  def ensure_registered(clazz):
    if clazz._adapters_registered:
      return
    clazz._register_custom_adapters_and_converters()
    clazz._adapters_registered = True

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
    return time_util.parse_datetime_with_tz(ts_str)
