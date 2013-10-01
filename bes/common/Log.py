#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os.path as path, os, re, sys, syslog, traceback, unittest

from datetime import datetime
from threading import Lock
from threading import Thread

from Decorator import synchronized_function

from ThreadUtil import ThreadUtil
from StringUtil import StringUtil
from ObjectUtil import ObjectUtil

import logging as pylog

_log_lock = Lock()

class Log(object):
  'Log'

  CRITICAL = 2
  ERROR = 3
  WARNING = 4
  INFO = 5
  DEBUG = 6

  DEFAULT_LEVEL = ERROR
  DEFAULT_LOG_FP = sys.stdout

  _level_to_string = {
    CRITICAL: 'critical', ERROR: 'error', WARNING: 'warning',
    INFO: 'info', DEBUG: 'debug'
  }

  _string_to_level = {
    'critical': CRITICAL, 'error': ERROR, 'warning': WARNING,
    'info': INFO, 'debug': DEBUG
  }

  _tag_levels = {}
  _level = DEFAULT_LEVEL
  _log_fp = DEFAULT_LOG_FP

  @classmethod
  @synchronized_function(_log_lock)
  def log(clazz, tag, level, message):
    'Log'
    tag_level = clazz.__get_tag_level(tag)
    #print "tag=%s; level=%d; tag_level=%d" % (tag, level, tag_level)
    if level > tag_level:
      return
    m = clazz.__make_message(tag, level, message)
    clazz._log_fp.write(m + '\n')
    clazz._log_fp.flush()
#    print m

  @classmethod
  def log_c(clazz, tag, message):
    'Log and CRITICAL message.'
    clazz.log(tag, clazz.CRITICAL, message)

  @classmethod
  def log_e(clazz, tag, message):
    'Log and ERROR message.'
    clazz.log(tag, clazz.ERROR, message)

  @classmethod
  def log_w(clazz, tag, message):
    'Log and WARNING message.'
    clazz.log(tag, clazz.WARNING, message)

  @classmethod
  def log_i(clazz, tag, message):
    'Log and INFO message.'
    clazz.log(tag, clazz.INFO, message)

  @classmethod
  def log_d(clazz, tag, message):
    'Log and DEBUG message.'
    clazz.log(tag, clazz.DEBUG, message)

  @classmethod
  def __make_message(clazz, tag, level, message):
    timestamp = str(datetime.now())
    pid = os.getpid()
    tid = ThreadUtil.gettid()
    process_info = '[%s.%s]' % (str(pid), str(tid))
    tag_info = '(%s.%s)' % (tag, clazz.level_to_string(level).upper())
    return "%s %s %s %s" % (timestamp, process_info, tag_info, message)

  @classmethod
  def parse_level(clazz, level):
    'Parse the level string and returns its integer value.'
    if level in [ clazz.CRITICAL, clazz.ERROR, clazz.WARNING, clazz.INFO, clazz.DEBUG ]:
      return level
    return clazz._string_to_level.get(level.lower(), clazz.INFO)

  @classmethod
  def level_to_string(clazz, level):
    'Return the level as a string.'
    return clazz._level_to_string.get(level, 'info')

  @classmethod
  @synchronized_function(_log_lock)
  def get_tag_level(clazz, tag):
    'Return the level for a tag with synchronization.'
    return clazz.__get_tag_level(tag)

  @classmethod
  def __get_tag_level(clazz, tag):
    'Return the level for a tag.'
    level = clazz._tag_levels.get(tag, None)
    if not level:
      clazz._tag_levels[tag] = clazz._level
      return clazz._level
    return level

  @classmethod
  @synchronized_function(_log_lock)
  def set_tag_level(clazz, tag, level):
    'Set the level for the given tag.'
    clazz.__configure(tag, level)

  @classmethod
  @synchronized_function(_log_lock)
  def set_tag_level_all(clazz, level):
    'Set the level for all the tag.'
    clazz.__configure('all', level)

  @classmethod
  @synchronized_function(_log_lock)
  def set_level(clazz, level):
    'Set the global level.'
    clazz._level = level

  @classmethod
  @synchronized_function(_log_lock)
  def get_level(clazz):
    'Return the global level.'
    return clazz._level

  @classmethod
  @synchronized_function(_log_lock)
  def configure(clazz, args):
    'Configure levels.'
    if isinstance(args, (str, unicode)):
      if args in clazz._string_to_level.keys():
        args = 'all=%s level=%s' % (args, args)
    args = StringUtil.flatten(args)
    flat = re.sub('\s*=\s*', '=', args)
    flat = re.sub('\s+', ' ', flat)
    parts = flat.split(' ')
    for part in parts:
      kv = part.partition('=')
      clazz.__configure(kv[0], kv[2])

  @classmethod
  def __configure(clazz, key, value):
    'Configure levels.'
    if key == 'level':
      clazz._level = clazz.parse_level(value)
    elif key == 'all':
      level = clazz.parse_level(value)
      for key in clazz._tag_levels.keys():
        clazz._tag_levels[key] = level
    elif key == 'reset':
      clazz.__configure('level', clazz.DEFAULT_LEVEL)
      clazz.__configure('all', clazz._level)
      clazz.__configure('file', clazz.DEFAULT_LOG_FP)
    elif key == 'file':
      if isinstance(value, file):
        clazz._log_fp = value
      else:
        clazz._log_fp = open(value, 'wa')
    else:
      clazz._tag_levels[key] = clazz.parse_level(value)

  @classmethod
  @synchronized_function(_log_lock)
  def set_log_file(clazz, f):
    'Set the log file to be f.  f can be a filename or a file object.'
    clazz.__configure('file', f)

  @classmethod
  @synchronized_function(_log_lock)
  def reset(clazz):
    'Parse the level string and returns its integer value.'
    clazz.__configure('reset', None)

  @staticmethod
  def _transplant_log(obj, level, message):
    Log.log(obj.tag, level, message)

  @staticmethod
  def _transplant_log_c(obj, message):
    Log.log_c(obj.tag, message)

  @staticmethod
  def _transplant_log_e(obj, message):
    Log.log_e(obj.tag, message)

  @staticmethod
  def _transplant_log_w(obj, message):
    Log.log_w(obj.tag, message)

  @staticmethod
  def _transplant_log_i(obj, message):
    Log.log_i(obj.tag, message)

  @staticmethod
  def _transplant_log_d(obj, message):
    Log.log_d(obj.tag, message)

  @staticmethod
  def _transplant_log_traceback(obj):
    Log.log_traceback(obj.tag)

  @staticmethod
  def _transplant_log_exception(obj, ex, show_traceback = True):
    Log.log_exception(obj.tag, ex, show_traceback)

  @classmethod
  def add_logging(clazz, obj, tag):
    'Add logging capabilities to obj.'
    obj.tag = tag
    if getattr(obj, 'log', None):
      return #raise RuntimeError('ObjectUtil already has logging capabilities.')
    ObjectUtil.add_method(clazz._transplant_log, obj, 'log')
    ObjectUtil.add_method(clazz._transplant_log_c, obj, 'log_c')
    ObjectUtil.add_method(clazz._transplant_log_e, obj, 'log_e')
    ObjectUtil.add_method(clazz._transplant_log_w, obj, 'log_w')
    ObjectUtil.add_method(clazz._transplant_log_i, obj, 'log_i')
    ObjectUtil.add_method(clazz._transplant_log_d, obj, 'log_d')
    ObjectUtil.add_method(clazz._transplant_log_traceback, obj, 'log_traceback')
    ObjectUtil.add_method(clazz._transplant_log_exception, obj, 'log_exception')

  @classmethod
  def log_traceback(clazz, tag):
    'Log a traceback as an error.'
    clazz.log_traceback_string(tag, traceback.format_exc())

  @classmethod
  def log_traceback_string(clazz, tag, ts):
    'Log a traceback string as an error.'
    for s in ts.split('\n'):
      clazz.log_e(tag, '  %s' % (s))

  @classmethod
  def log_exception(clazz, tag, ex, show_traceback = True):
    'Log an exception with optional traceback.'
    clazz.log_e(tag, 'Caught exception: %s %s' % (ex, str(type(ex))))
    if show_traceback:
      clazz.log_traceback(tag)

class LogFilter(pylog.Filter):
  'A python logging filter that steals the logs and sends them to Log instead'

  pylog_to_fateware_log = {
    pylog.CRITICAL: Log.CRITICAL,
    pylog.ERROR: Log.ERROR,
    pylog.WARNING: Log.WARNING,
    pylog.INFO: Log.INFO,
    pylog.DEBUG: Log.DEBUG,
  }

  def __init__(self, label):
    super(LogFilter, self).__init__(name = 'fateware_filter')
    self._label = label

  def filter(self, record):
    if self._label:
      message = '%s: %s' % (self._label, record.getMessage())
    else:
      message = record.getMessage()
    Log.log(record.module, self.__class__.pylog_to_fateware_log[record.levelno], message)
    return 0

class TestLog(unittest.TestCase):

  def test_defaults(self):
    Log.configure('foo=debug')
    Log.configure('bar=debug')
    Log.set_level(Log.DEBUG)
    Log.reset()
    self.assertEqual( Log.DEFAULT_LEVEL, Log.get_level() )
    self.assertEqual( Log.DEFAULT_LEVEL, Log.get_tag_level('foo') )
    self.assertEqual( Log.DEFAULT_LEVEL, Log.get_tag_level('bar') )

  def test_parse_level(self):
    self.assertEqual( Log.CRITICAL, Log.parse_level('critical') )
    self.assertEqual( Log.DEBUG, Log.parse_level('debug') )
    self.assertEqual( Log.ERROR, Log.parse_level('error') )
    self.assertEqual( Log.INFO, Log.parse_level('info') )
    self.assertEqual( Log.WARNING, Log.parse_level('warning') )

    self.assertEqual( Log.INFO, Log.parse_level('caca') )
    self.assertEqual( Log.INFO, Log.parse_level('') )
    self.assertEqual( Log.INFO, Log.INFO )

    self.assertEqual( Log.CRITICAL, Log.CRITICAL )
    self.assertEqual( Log.DEBUG, Log.DEBUG )
    self.assertEqual( Log.ERROR, Log.ERROR )
    self.assertEqual( Log.INFO, Log.INFO )
    self.assertEqual( Log.WARNING, Log.WARNING )

  def test_configure(self):
    Log.reset()
    Log.configure('foo=debug')
    self.assertEqual( Log.DEBUG, Log.get_tag_level('foo') )
    Log.configure('all=info')
    self.assertEqual( Log.INFO, Log.get_tag_level('foo') )

    self.assertEqual( Log.DEFAULT_LEVEL, Log.get_level() )
    Log.configure('level=critical')
    self.assertEqual( Log.INFO, Log.get_tag_level('foo') )
    self.assertEqual( Log.CRITICAL, Log.get_level() )

if __name__ == "__main__":
  unittest.main()
