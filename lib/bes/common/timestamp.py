#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from datetime import datetime, timedelta, tzinfo

import time

from bes.common.check import check

class timestamp(object):
  'Class to deal with timestamps'

  class utc(tzinfo):
    'UTC tzinfo'

    def utcoffset(self, dt):
      return timedelta(0)

    def tzname(self, dt):
      return 'UTC'
      
    def dst(self, dt):
      return timedelta(0)
  
  @classmethod
  def to_string(clazz, when, delimiter = '-', microsecond = False, timezone = None):
    '''
    Return a datetime object as a timestamp string in the form:
      1999-01-01-01-01-01-000001-UTC
    Where microsecond and timezone are optional.  If timezone is not None, then
    microsecond is assumed to be True.
    '''
    check.check(when, datetime)
    fmt = [ '%Y', '%m', '%d', '%H', '%M', '%S' ]
    if microsecond or timezone:
      fmt.append('%f')
    if timezone:
      fmt.append(timezone)
    return when.strftime(delimiter.join(fmt))

  @classmethod
  def parse(clazz, ts, delimiter = '-'):
    '''
    Parse a timestamp into a into a datetime object.
    Timestamp should be in the form:
      1999-01-01-01-01-01-000001-UTC
    Where only the year, month and day are mandatory.
    All other parts are optional.
    Only UTC time is currently supported.
    '''
    check.check_string(ts)
    parts = ts.split(delimiter)
    if len(parts) < 3:
      raise ValueError('Timestamp should have at least 3 parts (YEAR-MONTH-DAY): {}'.format(ts))
    year = clazz._pop_int(parts)
    month = clazz._pop_int(parts)
    day = clazz._pop_int(parts)
    hour = clazz._pop_int(parts)
    minute = clazz._pop_int(parts)
    second = clazz._pop_int(parts)
    microsecond = clazz._pop_int(parts)
    #tzinfo = clazz.utc()
    return datetime(year = year, month = month, day = day,
                    hour = hour, minute = minute, second = second,
                    microsecond = microsecond) #, tzinfo = tzinfo)

  @classmethod
  def _pop_int(clazz, l):
    'Pop an item from a list and convert it to int or 0 if list is empty.'
    try:
      return int(l.pop(0))
    except IndexError as ex:
      return 0
