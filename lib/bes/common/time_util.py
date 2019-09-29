#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from datetime import datetime
import time

from bes.common.check import check

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
