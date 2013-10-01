#!/usr/bin/env python
#-*- coding:utf-8 -*-

import traceback

from Log import Log

class Debug(object):
  'Debug'

  @classmethod
  def log_traceback(clazz, tag):
    'Log the traceback.'
    trace = traceback.format_exc().split('\n')
    for t in trace:
      Log.log_e(tag, '  %s' % (t))

  @classmethod
  def log_exception(clazz, tag, ex, show_traceback = True):
    'Log the traceback.'
    Log.log_e(tag, 'Caught exception: %s %s' % (ex, str(type(ex))))
    if show_traceback:
      clazz.log_traceback(tag)
