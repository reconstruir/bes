import sqlite3

from ..system.log import logger
from ..system.check import check

class sqlite_boolean_adapter_converter(object):

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
    sqlite3.register_adapter(bool, clazz._boolean_adapt)
    sqlite3.register_converter('boolean', clazz._boolean_convert)

  @classmethod
  def _boolean_adapt(clazz, value):
    """Convert Python boolean to SQLite-compatible INTEGER."""
    check.check_bool(value)
    int_value = 1 if value else 0
    clazz._log.log_d(f'_boolean_adapt: value={value} -> int_value={int_value}')
    return int_value

  @classmethod
  def _boolean_convert(clazz, value_bytes):
    """Convert SQLite INTEGER (0 or 1) back to Python boolean."""
    check.check_bytes(value_bytes)
    int_value = int(value_bytes.decode('utf-8'))
    bool_value = bool(int_value)
    clazz._log.log_d(f'_boolean_convert: value_bytes={value_bytes} -> bool_value={bool_value}')
    return bool_value
