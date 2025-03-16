#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import sqlite3

from .sqlite_datetime_adapter_converter import sqlite_datetime_adapter_converter
from .sqlite_boolean_adapter_converter import sqlite_boolean_adapter_converter
from .sqlite_json_adapter_converter import sqlite_json_adapter_converter

class sqlite_connection(sqlite3.Connection):

  sqlite_boolean_adapter_converter.ensure_registered()
  sqlite_datetime_adapter_converter.ensure_registered()
  sqlite_json_adapter_converter.ensure_registered()
