#!/usr/bin/env python
#-*- coding:utf-8 -*-

from datetime import datetime

class time_util(object):
  'Time util'

  @classmethod
  def timestamp(clazz, delimiter = '-', milliseconds = True):
    'Return a timestamp string in the form YYYY-MM-DD-HH-MM-SS.'
    delimiter = delimiter or ''
    fmt = [ '%Y', '%m', '%d', '%H', '%M', '%S' ]
    if milliseconds:
      fmt.append('%f')
    return datetime.now().strftime(delimiter.join(fmt))
