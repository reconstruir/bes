#!/usr/bin/env python
#-*- coding:utf-8 -*-

from bes.common import json_util
from mac_address import mac_address

class mac_address_lookup(object):
  'Lookup mac address by alias.'

  @classmethod
  def get_alias(clazz, filename, addr):
    'Lookup the alias for the given mac address or None if not found.'
    addr = mac_address.normalize_mac_address(addr)
    data = clazz.__db_load(filename)
    return data.get(addr, None)

  @classmethod
  def get_address(clazz, filename, alias):
    'Lookup the address for the given alias None if not found.'
    data = clazz.__db_load(filename)
    for key, value in data.items():
      if value == alias:
        return key
    return None

  @classmethod
  def put_alias(clazz, filename, addr, alias):
    'Put the alias for address into the db.'
    addr = mac_address.normalize_mac_address(addr)
    data = clazz.__db_load(filename)
    data[addr] = alias
    json_util.save_file(filename, data, indent = 2)

  @classmethod
  def __db_load(clazz, filename):
    'Load the cache.'
    try:
      return json_util.read_file(filename) or {}
    except IOError, ex:
      return {}
