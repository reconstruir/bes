#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import sqlite3
import json

from ..system.log import logger
from ..system.check import check
from ..common.time_util import time_util

class sqlite_json_adapter_converter(object):

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
    sqlite3.register_adapter(dict, clazz._json_adapt)
    sqlite3.register_converter('BES_JSON', clazz._json_convert)

  @classmethod
  def _json_adapt(clazz, d):
    check.check_dict(d)

    json_text = json.dumps(d)
    clazz._log.log_d(f'_json_adapt: d={d} json_text={json_text}')
    return json_text

  @classmethod
  def _json_convert(clazz, json_bytes):
    check.check_bytes(json_bytes)

    json_text = json_bytes.decode('utf-8')
    return json.loads(json_text)
