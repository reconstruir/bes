#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from datetime import datetime
import time

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

  _FORMAT = ( '%Y', '%m', '%d', '%H', '%M', '%S' )
  _FORMAT_WITH_MS = _FORMAT + ( '%f', ) 
  
  @classmethod
  def format_for_timestamp(clazz, when, delimiter = '-', milliseconds = False, timezone = False):
    'Format a datetime object for a timestamp.'
    delimiter = delimiter or ''
    fmt = [ '%Y', '%m', '%d', '%H', '%M', '%S' ]
    if milliseconds:
      fmt.append('%f')
    if timezone:
      fmt.append(clazz.timezone())
    return when.strftime(delimiter.join(fmt))

  @classmethod
  def timestamp_parse(clazz, when, delimiter = '-', milliseconds = False, timezone = False):
    'Parse a timestamp in the form 1999-01-01-01-01-01 to a datetime object.'
    fmt = clazz._FORMAT_WITH_MS if  milliseconds else clazz._FORMAT
    fmt_delim = delimiter.join(fmt)
    return datetime.strptime(when, fmt_delim)
