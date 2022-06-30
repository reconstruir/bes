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
