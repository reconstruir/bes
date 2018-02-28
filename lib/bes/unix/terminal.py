#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os, sys
from collections import namedtuple
from bes.common import size as bes_size
from bes.system import execute

class terminal(object):
  'Stuff to deal with unix terminals'

  @classmethod
  def width(clazz):
    'Return the width of the current terminal.  Must be running under a tty.'
    return clazz.size().width

  @classmethod
  def height(clazz):
    'Return the height of the current terminal.  Must be running under a tty.'
    return clazz.size().height

  @classmethod
  def size(clazz):
    'Return the size of the current terminal.  Must be running under a tty.'
    tty = clazz.tty()
    with open(tty, 'r') as f:
      if not os.isatty(f.fileno()):
        raise RuntimeError('not a terminal: %s' % (tty))
      s = os.popen('stty size < %s' % (tty), 'r').read().split()
      return bes_size(int(s[1]), int(s[0]))

  @classmethod
  def tty(clazz):
    'Return the current tty for this process.'
    return execute.execute('tty').stdout.strip()
