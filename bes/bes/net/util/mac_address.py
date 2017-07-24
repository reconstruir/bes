#!/usr/bin/env python
#-*- coding:utf-8 -*-

from bes.common import json_util

import re

class mac_address(object):
  'mac_address'

  @classmethod
  def parse_mac_address(clazz, address):
    '''
    Parse a mac address in the forms 00:00:00:00:00:00, 00-00-00-00-00-00, 0:0:0:0:0:0, 0-0-0-0-0-0
    Returns a list'
    '''
    r = clazz.__get_mac_re().findall(address)
    if len(r) != 1:
      return None
    return list(r[0])

  @classmethod
  def is_valid(clazz, address):
    '''
    Return True if address is a valid mac address.
    '''
    address = clazz.normalize_mac_address(address)
    if not address:
      return False
    parsed = clazz.parse_mac_address(address)
    if not parsed:
      return False
    try:
      for digit in parsed:
        digit.decode('HEX')
    except Exception, ex:
      return False
    return True

  @classmethod
  def normalize_mac_address(clazz, address):
    '''
    Format a mac address for pretty print.
    '''
    parsed = clazz.parse_mac_address(address.lower())
    if not parsed:
      return None
    filled = [ part.zfill(2) for part in parsed ]
    return ':'.join(filled)
    
  __MAC_RE_OCTET_EXPRESSION = r'([0-9a-fA-F]{1,2})'
  __MAC_RE_SEPARATOR_EXPRESSION = r'[-:]'
  __MAC_RE_EXPRESSION_parts = [ __MAC_RE_OCTET_EXPRESSION ] * 6
  __MAC_RE_EXPRESSION = __MAC_RE_SEPARATOR_EXPRESSION.join(__MAC_RE_EXPRESSION_parts)
  __MAC_RE = None

  @classmethod
  def __get_mac_re(clazz):
    if not clazz.__MAC_RE:
      clazz.__MAC_RE = re.compile(clazz.__MAC_RE_EXPRESSION)
    return clazz.__MAC_RE
