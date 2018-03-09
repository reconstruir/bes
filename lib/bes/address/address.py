#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple
from bes.common import string_util
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
      v = s.split(',')
    else:
      v = string_util.split_by_white_space(s)
    print v
    return None

  @classmethod
  def state_is_valid(clazz, s):
    'Return True if s is a valid state.  Ignores case.'
    return s.upper() in USA_STATES
