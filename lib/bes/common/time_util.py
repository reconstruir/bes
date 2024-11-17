#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple
from datetime import datetime

import time
import math

from ..system.check import check

class time_util(object):
  'Time util'

  @classmethod
  def timestamp(clazz, delimiter = '-', milliseconds = True, timezone = False, when = None):
    'Return a timestamp string in the form YYYY-MM-DD-HH-MM-SS.'
    check.check_string(delimiter)
    check.check_bool(milliseconds)
    check.check_bool(timezone)
    check.check(when, datetime, allow_none = True)
    
    delimiter = delimiter or ''
    fmt = [ '%Y', '%m', '%d', '%H', '%M', '%S' ]
    when = when or datetime.now()
    if milliseconds:
      fmt.append('%f')
    if timezone:
      fmt.append(clazz.timezone())
    return when.strftime(delimiter.join(fmt))

  @classmethod
  def timezone(clazz):
    'Return the current timezone (ie PST).'
    return time.strftime('%Z')

  _ms_tuple = namedtuple('_ms_tuple', 'hours, minutes, seconds')
  @classmethod
  def ms_to_tuple(clazz, ms):
    check.check_int(ms)
    
    seconds = math.floor(ms / 1000) % 60
    minutes = math.floor(ms / (1000 * 60)) % 60
    hours = math.floor(ms / (1000 * 60 * 60)) % 24
    return clazz._ms_tuple(hours, minutes, seconds)

  @classmethod
  def ms_to_string(clazz, ms, show_hours = True):
    check.check_int(ms)

    t = clazz.ms_to_tuple(ms)
    if t.hours or show_hours:
      return '{}:{}:{}'.format(str(t.hours).zfill(2),
                               str(t.minutes).zfill(2),
                               str(t.seconds).zfill(2))
    else:
      return '{}:{}'.format(str(t.minutes).zfill(2),
                            str(t.seconds).zfill(2))

  @classmethod
  def timestamp_iso8601(clazz, when, milliseconds = True):
    check.check(when, datetime)
    fmt = [ '%Y', '%m', '%d', '%H', '%M', '%S' ]
    fmt = '%Y-%m-%d %H:%M:%S'
    if milliseconds:
      fmt = fmt + ':%f'
    return when.strftime(fmt)

  @classmethod
  def parse_datetime_with_tz(clazz, datetime_text):
    check.check_string(datetime_text)

    if '+' in datetime_text:
      tz_format = '%Y-%m-%d %H:%M:%S%z'
    else:
      tz_format = '%Y-%m-%d %H:%M:%S'
    date = datetime.strptime(datetime_text, tz_format)
    return date
  
