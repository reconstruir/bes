#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import OrderedDict
import time
from bes.system import log

class debug_timer(object):
  '''
  A class to instrument code to time operations with nice hierarchical output
  From: https://www.darklaunch.com/2012/09/14/python-measure-elapsed-execution-time-timer-class
  '''
  
  if False:
    BOX_VERTICAL = u'\u2502'
    BOX_DOWN_AND_RIGHT = u'\u250c'
    BOX_UP_AND_RIGHT = u'\u2514'
  else:
    BOX_VERTICAL = u'|'
    BOX_DOWN_AND_RIGHT = u'|'
    BOX_UP_AND_RIGHT = u'L'

  def __init__(self, tag, level = 'debug', disabled = False):
    log.add_logging(self, tag)
    self._disabled = disabled
    if self._disabled:
      return
    self._level = log.parse_level(level)
    self.starts = OrderedDict()
    self.starts['start'] = time.time()
 
  def round(self, number):
    return '{0:>5} {1}'.format(int(number * 1000), 'ms')
 
  def columns(self, count):
    return u'{0}  '.format(self.BOX_VERTICAL) * count
 
  def start(self, thing):
    if self._disabled:
      return
    self.starts[thing] = time.time()
    self.log(self._level, u'{0} {1}{2} {3}'.format(' ' * 8, self.columns(len(self.starts) - 2), self.BOX_DOWN_AND_RIGHT, thing))
 
  def stop(self):
    if self._disabled:
      return
    thing, started = self.starts.popitem()
    elapsed = self.round(time.time() - started)
    self.log(self._level, u'{0} {1}{2} {3}'.format(elapsed, self.columns(len(self.starts) - 1), self.BOX_UP_AND_RIGHT, thing))
