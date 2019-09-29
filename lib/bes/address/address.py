#!/usr/bin/env python3
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple
from bes.common.string_util import string_util
from .usa_states import USA_STATES

class address(object):

  _city_state = namedtuple('_city_state', 'city,state')
  
  @classmethod
  def parse_city_and_state(clazz, s):
    '''
    Parse text in the form off "City, ST" "City ST" "ST, City" "ST City" for city and state
    or None if the state or format cannot be determined.
    '''
    if ',' in s:
      parts = s.split(',')
    else:
      parts = string_util.split_by_white_space(s)
    state_index = clazz._find_state_index(parts)
    if state_index < 0:
      return None
    state = parts[state_index].strip()
    parts[state_index] = ''
    city = ' '.join(parts).strip()
    return clazz._city_state(city, state)

  @classmethod
  def state_is_valid(clazz, s):
    'Return True if s is a valid state.  Ignores case.'
    return s.upper() in USA_STATES

  @classmethod
  def _find_state_index(clazz, parts):
    for i, possible_state in enumerate(parts):
      if clazz.state_is_valid(possible_state.strip()):
        return i
    return -1
      
  
