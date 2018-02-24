#!/usr/bin/env python
#-*- coding:utf-8 -*-

from datetime import datetime
from pytz import reference

class time_util(object):
  'Time util'

  @classmethod
  def timestamp(clazz, delimiter = '-', milliseconds = True, timezone = False):
    'Return a timestamp string in the form YYYY-MM-DD-HH-MM-SS.'
    delimiter = delimiter or ''
    fmt = [ '%Y', '%m', '%d', '%H', '%M', '%S' ]
    now = datetime.now()
    if milliseconds:
      fmt.append('%f')
    if timezone:
      fmt.append(reference.LocalTimezone().tzname(now))
    return now.strftime(delimiter.join(fmt))
