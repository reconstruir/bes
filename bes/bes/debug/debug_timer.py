#!/usr/bin/env python
#-*- coding:utf-8 -*-

from collections import OrderedDict
import logging
import time

# From: https://www.darklaunch.com/2012/09/14/python-measure-elapsed-execution-time-timer-class

class debug_timer(object):
  def __init__(self):
    self.starts = OrderedDict()
    self.starts['start'] = time.time()
 
  def round(self, number):
    return '{0:>5} {1}'.format(int(number * 1000), 'ms')
 
  def columns(self, count):
    return u'{0}  '.format(u'\u2502') * count
 
  def start(self, thing):
    self.starts[thing] = time.time()
    logging.debug(u'{0} {1}{2} {3}'.format(' ' * 8, self.columns(len(self.starts) - 2), u'\u250c', thing))
 
  def stop(self):
    thing, started = self.starts.popitem()
    elapsed = self.round(time.time() - started)
    logging.debug(u'{0} {1}{2} {3}'.format(elapsed, self.columns(len(self.starts) - 1), u'\u2514', thing))
