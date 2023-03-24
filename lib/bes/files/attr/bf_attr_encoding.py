#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import json

from datetime import datetime

from bes.common.number_util import number_util
from bes.common.bool_util import bool_util
from bes.common.json_util import json_util

from bes.system.check import check

class bf_attr_encoding(object):

  @classmethod
  def decode_int(clazz, value):
    'Decode an int'
    check.check_bytes(value)
    
    return number_util.to_int(value.decode('utf-8'))

  @classmethod
  def encode_int(clazz, value):
    'Decode an int'
    check.check_int(value)

    return str(value).encode('utf-8')
  
  @classmethod
  def decode_float(clazz, value):
    'Decode an int'
    check.check_bytes(value)
    
    return number_util.to_float(value.decode('utf-8'))

  @classmethod
  def encode_float(clazz, value):
    'Decode an float'
    check.check_number(value)

    return str(value).encode('utf-8')
  
  @classmethod
  def decode_string(clazz, value):
    'Decode a string'
    check.check_bytes(value)
    
    return value.decode('utf-8')

  @classmethod
  def encode_string(clazz, value):
    'Decode an string'
    check.check_string(value)

    return value.encode('utf-8')
  
  @classmethod
  def decode_bool(clazz, value, allow_none = False):
    'Decode an bool'
    check.check_bytes(value)
    check.check_bool(allow_none)
    
    s = value.decode('utf-8')
    if allow_none and s == '':
      return None
    return bool_util.parse_bool(s)

  @classmethod
  def encode_bool(clazz, value, allow_none = False):
    'Decode an bool'
    check.check_bool(allow_none)
    check.check_bool(value, allow_none = allow_none)

    if value == None:
      return clazz.encode_string('')
    return str(value).encode('utf-8')

  @classmethod
  def decode_datetime(clazz, value):
    'Decode a date'
    check.check_bytes(value)

    string_value = clazz.decode_string(value)
    timestamp = float(string_value)
    return datetime.fromtimestamp(timestamp)
    
  @classmethod
  def encode_datetime(clazz, value):
    'Decode an date'
    check.check_datetime(value)

    return clazz.encode_string(str(value.timestamp()))

  @classmethod
  def decode_json(clazz, value):
    'Decode bytes as json'
    check.check_bytes(value)

    string_value = clazz.decode_string(value)
    return json.loads(string_value)
    
  @classmethod
  def encode_json(clazz, value):
    'Encode a dict as json'
    check.check_dict(value)

    string_value = json_util.to_json(value, indent = 2, sort_keys = False)
    return clazz.encode_string(string_value)
  
