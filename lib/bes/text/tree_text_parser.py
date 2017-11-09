#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common import node
from bes.compat import StringIO
from collections import namedtuple

class stack(object):
  item = namedtuple('item', 'depth,line')

  def __init__(self):
    self._stack = []

  def push(self, depth, line):
    self._stack.append(self.item(depth, line))

  def pop(self):
    return self._stack.pop()

  def peek(self):
    return self._stack[-1]

  def empty(self):
    return len(self._stack) == 0

  def path(self):
    return [ i.line for i in self._stack ]

  def __str__(self):
    buf = StringIO()
    for i, item in enumerate(self._stack):
      if i != 0:
        buf.write('/')
      buf.write(str(item.depth or 0))
      buf.write(':')
      buf.write(item.line)
    return buf.getvalue()
  
class tree_text_parser(object):

  @classmethod
  def parse(clazz, text):
    result = node('root')
    st = stack()
    current_indent = None
    for line in clazz._lines(text):
      indent = clazz._count_indent(line)
      line = line.strip()
      if current_indent is None or indent > current_indent:
        st.push(indent, line)
      else:
        while not st.empty() and st.peek().depth >= indent:
          st.pop()
        st.push(indent, line)
      result.ensure_path(st.path())
      current_indent = indent
    return result
  
  @classmethod
  def _lines(clazz, text):
    lines = [ line for line in text.split('\n') ]
    return [ line for line in lines if line ]

  @classmethod
  def _count_indent(clazz, s):
    count = 0
    for c in s:
      if c.isspace():
        count += 1
      else:
        break
    return count

