#!/usr/bin/env python
#-*- coding:utf-8 -*-

from datetime import datetime
import time

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
      fmt.append(clazz.timezone())
    return now.strftime(delimiter.join(fmt))

  @classmethod
  def timezone(clazz):
    'Return the current timezone (ie PST).'
    return time.strftime('%Z')
