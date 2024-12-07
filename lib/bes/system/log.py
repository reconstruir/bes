#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import fnmatch, os, os.path as path, re, sys, time, traceback
import inspect

from datetime import datetime
import threading
import multiprocessing

from .add_method import add_method
from .check import check
from .compat import compat
from .console import console as system_console
from .thread_id import thread_id

from ._detail.log_writer_list import log_writer_list

import logging as pylog

class log(object):
  'Alternative to python logging.'

  CRITICAL = 2
  ERROR = 3
  WARNING = 4
  INFO = 5
  DEBUG = 6

  DEFAULT_LEVEL = ERROR

  FORMAT_FULL = '${timestamp}${space}[${process_id}.${thread_id}]${space}(${tag}.${level})${padding}${space}${message}'
  FORMAT_NOTIME = '${space}[${process_id}.${thread_id}]${space}(${tag}.${level})${padding}${space}${message}'
  FORMAT_BRIEF = '${timestamp_brief}${space}(${tag}.${level})${padding}${space}${message}'
  FORMAT_VERY_BRIEF = '(${tag}.${level})${padding}${space}${message}'

  _PADDING_CHAR = ' '
  _DEFAULT_FORMAT = FORMAT_FULL
  _FORMATS = {
    'notime': FORMAT_NOTIME,
    'full': FORMAT_FULL,
    'brief': FORMAT_BRIEF,
    'very_brief': FORMAT_VERY_BRIEF,
    }

  _level_to_string = {
    CRITICAL: 'critical', ERROR: 'error', WARNING: 'warning', INFO: 'info', DEBUG: 'debug'
  }

  _string_to_level = {
    'critical': CRITICAL, 'error': ERROR, 'warning': WARNING, 'info': INFO, 'debug': DEBUG
  }

  _longest_level_length = max([ len(level) for level in _string_to_level.keys() ])
  
  _tag_levels = {}
  _level = DEFAULT_LEVEL
  _log_writer = log_writer_list()
  _log_lock = threading.Lock()
  _format = _DEFAULT_FORMAT
  _log_config_patterns = {}
  _longest_tag_length = 0
  _tag_width = None
  _filters = []

  @classmethod
  def log(clazz, tag, level, message, multi_line = False):
    'log'
    clazz._log_lock.acquire()
    try:
      clazz._do_log_i(tag, level, message, multi_line)
    except Exception as ex:
      clazz._log_writer.write('Unexpected logging error: %s\n' % (str(ex)))
      clazz._log_writer.flush()
    clazz._log_lock.release()

  @classmethod
  def _do_log_i(clazz, tag, level, message, multi_line):
    'Do the logging work.'
    tag_level = clazz._get_tag_level(tag)
    if level > tag_level:
      return
    timestamp = datetime.now()
    if multi_line:
      lines = message.split(os.linesep)
      messages = [ clazz._make_message_i(tag, level, line, timestamp) for line in lines ]
    else:
      messages = [ clazz._make_message_i(tag, level, message, timestamp) ]
    for m in messages:
      m = clazz._filter_string_i(m, clazz._filters)
      clazz._log_writer.write(m + os.linesep)
    clazz._log_writer.flush()
      
  @classmethod
  def log_c(clazz, tag, message, multi_line = False):
    'Log and CRITICAL message.'
    clazz.log(tag, clazz.CRITICAL, message, multi_line = multi_line)

  @classmethod
  def log_e(clazz, tag, message, multi_line = False):
    'Log and ERROR message.'
    clazz.log(tag, clazz.ERROR, message, multi_line = multi_line)

  @classmethod
  def log_w(clazz, tag, message, multi_line = False):
    'Log and WARNING message.'
    clazz.log(tag, clazz.WARNING, message, multi_line = multi_line)

  @classmethod
  def log_i(clazz, tag, message, multi_line = False):
    'Log and INFO message.'
    clazz.log(tag, clazz.INFO, message, multi_line = multi_line)

  @classmethod
  def log_d(clazz, tag, message, multi_line = False):
    'Log and DEBUG message.'
    clazz.log(tag, clazz.DEBUG, message, multi_line = multi_line)

  @classmethod
  def _make_message_i(clazz, tag, level, message, timestamp):
    level = clazz.level_to_string(level).upper()
    current_width = len(tag) + len(level)
    longest_tag_length = clazz._tag_width or clazz._longest_tag_length
    max_width = clazz._longest_level_length + longest_tag_length
    delta = max_width - current_width
    delta = 1  # FIXME ?
    process_name = multiprocessing.current_process().name
    values = {
      'timestamp': clazz._format_timestamp(timestamp),
      'timestamp_brief': clazz._format_timestamp_brief(timestamp),
      'process_id': process_name, #str(os.getpid()),
      'thread_id': str(thread_id.thread_id()),
      'tag': tag,
      'level': level,
      'message': message,
      'space': ' ',
      'padding': delta * clazz._PADDING_CHAR
    }
    result = clazz._format
    for key, value in values.items():
      var = '${%s}' % (key)
      result = result.replace(var, value)
    return result

  @classmethod
  def _format_timestamp(clazz, timestamp):
    fmt = '%Y_%m_%d-%H:%M:%S-{TZ}'.format(TZ = time.strftime('%Z'))
    return timestamp.strftime(fmt)

  @classmethod
  def _format_timestamp_brief(clazz, timestamp):
    fmt = '%H:%M:%S'
    return timestamp.strftime(fmt)

  @classmethod
  def timezone(clazz):
    'Return the current timezone (ie PST).'
    return time.strftime('%Z')
  
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
  def get_tag_level(clazz, tag):
    'Return the level for a tag with synchronization.'
    clazz._log_lock.acquire()
    rv = clazz._get_tag_level(tag)
    clazz._log_lock.release()
    return rv

  @classmethod
  def _get_tag_level(clazz, tag):
    'Return the level for a tag.'
    level = clazz._tag_levels.get(tag, None)
    if not level:
      clazz._tag_levels[tag] = clazz._level
      return clazz._level
    return level

  @classmethod
  def set_tag_level(clazz, tag, level):
    'Set the level for the given tag.'
    clazz._log_lock.acquire()
    clazz._configure_i(tag, level)
    clazz._log_lock.release()

  @classmethod
  def set_tag_level_all(clazz, level):
    'Set the level for all the tag.'
    clazz._log_lock.acquire()
    clazz._configure_i('all', level)
    clazz._log_lock.release()

  @classmethod
  def set_level(clazz, level):
    'Set the global level.'
    clazz._log_lock.acquire()
    clazz._level = level
    clazz._log_lock.release()

  @classmethod
  def get_level(clazz):
    'Return the global level.'
    clazz._log_lock.acquire()
    rv = clazz._level
    clazz._log_lock.release()
    return rv

  @classmethod
  def configure(clazz, args):
    'Configure levels.'
    clazz._log_lock.acquire()
    if isinstance(args, compat.STRING_TYPES):
      if args in clazz._string_to_level.keys():
        args = 'all=%s level=%s' % (args, args)
    args = clazz._flatten(args)
    # remove white spaces around the equal sign: 'foo  =  bar' => 'foo=bar'
    flat = re.sub(r'\s*=\s*', '=', args)
    # coalesce multiple white spaces into just one space 
    flat = re.sub(r'\s+', ' ', flat)
    parts = flat.split(' ')
    for part in parts:
      key, sep, value = part.partition('=')
      clazz._configure_i(key, value)
    clazz._log_lock.release()

  @classmethod
  def add_filter(clazz, filter_function):
    'Configure levels.'
    check.check_callable(filter_function)
    
    clazz._log_lock.acquire()
    clazz._filters.append(filter_function)
    clazz._log_lock.release()

  @classmethod
  def _filter_string_i(clazz, s, filters):
    for next_filter in filters:
      s = next_filter(s)
    return s
    
  @classmethod
  def _flatten(clazz, s, delimiter = ' '):
    'Flatten the given collection to a string.'
    'If s is already a string just return it.'
    if isinstance(s, compat.STRING_TYPES):
      return s
    if isinstance(s, list):
      return delimiter.join(s)
    raise RuntimeError('Not a string or list')

  @classmethod
  def _configure_i(clazz, key, value):
    'Configure logging.'
    if key == 'level':
      clazz._level = clazz.parse_level(value)
    elif key == 'all':
      level = clazz.parse_level(value)
      for key in clazz._tag_levels.keys():
        clazz._tag_levels[key] = level
    elif key == 'reset':
      clazz._configure_i('level', clazz.DEFAULT_LEVEL)
      clazz._configure_i('all', clazz._level)
      clazz._log_writer.reset()
    elif key in [ 'output', 'out', 'o' ]:
      clazz._log_writer.configure(value)
    elif key == 'dump':
      lines = [ '%s: %s' % (key, clazz._level_to_string.get(level)) for key, level in sorted(clazz._tag_levels.items()) ]
      message = os.linesep.join(lines) + os.linesep
      clazz.output(message, console = True)
    elif key == 'format':
      clazz._format = clazz._FORMATS.get(value, value)
    elif key == 'width':
      clazz._tag_width = int(value)
    else:
      if clazz._key_is_fnmatch_pattern(key):
        clazz._log_config_patterns[key] = clazz.parse_level(value)
        clazz._update_levels_from_patterns()
      else:
        clazz._tag_levels[key] = clazz.parse_level(value)

  @classmethod
  def _update_levels_from_patterns(clazz):
    for pattern, level in clazz._log_config_patterns.items():
      for key in clazz._tag_levels.keys():
        if fnmatch.fnmatch(key, pattern):
          clazz._tag_levels[key] = level
        
  @classmethod
  def _update_longest_tag_length(clazz):
    clazz._longest_tag_length = max(len(key) for key in clazz._tag_levels.keys())
    
  _FNMATCH_CHARS = '.*?[]!'
  @classmethod
  def _key_is_fnmatch_pattern(clazz, key):
    for c in key:
      if c in clazz._FNMATCH_CHARS:
        return True
    return False
  
  @classmethod
  def output(clazz, message, console = False):
    system_console.output(message, console = console)
    
  @classmethod
  def console(clazz, message):
    clazz.output(message, console = True)
    
  @classmethod
  def set_log_file(clazz, filename):
    'Redirect logging to the file.'
    clazz._log_lock.acquire()
    clazz._log_writer.clear()
    clazz._log_writer.add_filename(filename)
    clazz._log_lock.release()

  @classmethod
  def reset(clazz):
    'Reset the log configuration to the defaults.'
    clazz._log_lock.acquire()
    clazz._configure_i('reset', None)
    clazz._log_lock.release()

  @staticmethod
  def _transplant_log(obj, level, message, multi_line = False):
    log.log(obj.bes_log_tag__, level, message, multi_line = multi_line)

  @staticmethod
  def _transplant_log_c(obj, message, multi_line = False):
    log.log_c(obj.bes_log_tag__, message, multi_line = multi_line)

  @staticmethod
  def _transplant_log_e(obj, message, multi_line = False):
    log.log_e(obj.bes_log_tag__, message, multi_line = multi_line)

  @staticmethod
  def _transplant_log_w(obj, message, multi_line = False):
    log.log_w(obj.bes_log_tag__, message, multi_line = multi_line)

  @staticmethod
  def _transplant_log_i(obj, message, multi_line = False):
    log.log_i(obj.bes_log_tag__, message, multi_line = multi_line)

  @staticmethod
  def _transplant_log_d(obj, message, multi_line = False):
    log.log_d(obj.bes_log_tag__, message, multi_line = multi_line)

  @staticmethod
  def _transplant_log_traceback(obj):
    log.log_traceback(obj.bes_log_tag__)

  @staticmethod
  def _transplant_log_exception(obj, ex, show_traceback = True):
    log.log_exception(obj.bes_log_tag__, ex, show_traceback)

  @classmethod
  def add_logging(clazz, obj, tag = None):
    'Add logging capabilities to obj via its class.'
    if type(obj) == type:
      object_class = obj
      tag = tag or object_class.__name__
    else:
      object_class = obj.__class__

    if getattr(object_class, 'bes_log_added__', False):
      return
      
    if getattr(object_class, 'log', None):
      raise RuntimeError('class already has a "log" method attribute: %s' % (object_class))
    
    if getattr(obj, 'log', None):
      raise RuntimeError('Object already has a "log" method attribute: %s' % (obj))
    
    tag = tag or object_class.__class__.__name__
    setattr(object_class, 'bes_log_tag__', tag)
    add_method(clazz._transplant_log, object_class, 'log')
    add_method(clazz._transplant_log_c, object_class, 'log_c')
    add_method(clazz._transplant_log_e, object_class, 'log_e')
    add_method(clazz._transplant_log_w, object_class, 'log_w')
    add_method(clazz._transplant_log_i, object_class, 'log_i')
    add_method(clazz._transplant_log_d, object_class, 'log_d')
    add_method(clazz._transplant_log_traceback, object_class, 'log_traceback')
    add_method(clazz._transplant_log_exception, object_class, 'log_exception')
    setattr(object_class, 'bes_log_added__', True)

    if tag not in clazz._tag_levels:
      clazz._tag_levels[tag] = clazz.DEFAULT_LEVEL

    clazz._update_levels_from_patterns()
    clazz._update_longest_tag_length()
    
  @classmethod
  def _default_tag(clazz, obj):
    'Return the default tag for obj.'
    assert obj
    if type(obj) == type:
      return obj.__name__
    return obj.__class__.__name__

  @classmethod
  def log_traceback(clazz, tag):
    'Log a traceback as an error.'
    clazz.log_traceback_string(tag, traceback.format_exc())

  @classmethod
  def log_traceback_string(clazz, tag, ts):
    'Log a traceback string as an error.'
    for s in ts.split(os.linesep):
      clazz.log_e(tag, '  %s' % (s))

  @classmethod
  def log_exception(clazz, tag, ex, show_traceback = True):
    'Log an exception with optional traceback.'
    clazz.log_e(tag, 'Caught exception: %s %s' % (ex, str(type(ex))))
    if show_traceback:
      clazz.log_traceback(tag)

class log_filter(pylog.Filter):
  'A python logging filter that steals the logs and sends them to Log instead'

  pylog_to_fateware_log = {
    pylog.CRITICAL: log.CRITICAL,
    pylog.ERROR: log.ERROR,
    pylog.WARNING: log.WARNING,
    pylog.INFO: log.INFO,
    pylog.DEBUG: log.DEBUG,
  }

  def __init__(self, label):
    super(log_filter, self).__init__(name = 'bes_filter')
    self._label = label

  def filter(self, record):
    if self._label:
      message = '%s: %s' % (self._label, record.getMessage())
    else:
      message = record.getMessage()
    log.log(record.module, self.__class__.pylog_to_fateware_log[record.levelno], message)
    return 0

_config = os.environ.get('BES_LOG', None)
if _config:
  log.configure(_config)
del _config

class logger(object):

  CRITICAL = log.CRITICAL
  ERROR = log.ERROR
  WARNING = log.WARNING
  INFO = log.INFO
  DEBUG = log.DEBUG
  
  def __init__(self, tag):
    self._tag = tag

  @property
  def tag(self):
    return self._tag
    
  def log(self, level, message, multi_line = False):
    log.log(self._tag, level, message, multi_line = multi_line)

  def log_c(self, message, multi_line = False):
    log.log_c(self._tag, message, multi_line = multi_line)

  def log_e(self, message, multi_line = False):
    log.log_e(self._tag, message, multi_line = multi_line)

  def log_w(self, message, multi_line = False):
    log.log_w(self._tag, message, multi_line = multi_line)

  def log_i(self, message, multi_line = False):
    log.log_i(self._tag, message, multi_line = multi_line)

  def log_d(self, message, multi_line = False):
    log.log_d(self._tag, message, multi_line = multi_line)

  def log_traceback(self):
    'Log a traceback as an error.'
    log.log_traceback(self._tag)

  def log_traceback_string(self, ts):
    'Log a traceback string as an error.'
    log.log_traceback_string(self._tag, ts)

  def log_exception(self, ex, show_traceback = True):
    'Log an exception with optional traceback.'
    log.log_exception(self._tag, ex, show_traceback = show_traceback)

  def configure(self, args):
    'Configure logging.'
    log.configure(args)

  def reset(self):
    'Reset logging.'
    log.reset()

  def log_method(self, level, depth = 1):
    '''
    Log a instance or clazz method including name and all arguments
    Please note this method is *slow*.  Around 50ms on a fast modern
    macbook pro.  So don't use it in performance sensitive code.
    '''
    current_frame = inspect.currentframe()
    caller_frame = current_frame
    for _ in range(0, depth):
      caller_frame = caller_frame.f_back
    args, _, _, values = inspect.getargvalues(caller_frame)
    args.pop(0)
    method_name = inspect.getframeinfo(caller_frame)[2]
    args_strings = [ '{}={}'.format(key, str(values[key]).replace(os.linesep, ' ')) for key in args ]
    msg = '{}: {}'.format(method_name, ' '.join(args_strings))
    self.log(level, msg, multi_line = True)

  def log_method_d(self):
    self.log_method(log.DEBUG, depth = 2)

  def log_method_i(self):
    self.log_method(log.INFO, depth = 2)

  def log_method_c(self):
    self.log_method(log.CRITICAL, depth = 2)
    
  def log_method_e(self):
    self.log_method(log.ERROR, depth = 2)
    
  def log_method_w(self):
    self.log_method(log.WARNING, depth = 2)
    
  critical = log_c
  debug = log_d
  info = log_i
  warning = log_w
