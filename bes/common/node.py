#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import StringIO
from collections import namedtuple

class node(object):

  def __init__(self, data):
    self.data = data
    self.children = []

  def __eq__(self, other):
    assert isinstance(other, node)
    return self.__dict__ == other.__dict__

  def __str__(self):
    return self.to_string(0)

  def add_child(self, data):
    n = node(data)
    self.children.append(n)
    return n

  def ensure_child(self, data):
    return self.caca_find_child(data) or self.add_child(data)

  def num_children(self):
    return len(self.children)
    
  def caca_find_child(self, data):
    for child in self.children:
      if child.data == data:
        return child
    return None

  find_result = namedtuple('find_result', 'depth,child')

  def find_children(self, func):
    return self._find_children(func, 0)

  def find_child(self, func):
    found = self._find_children(func, 0)
    if not found:
      return None
    return found[0].child

  def _find_children(self, func, depth):
    result = []
    for child in self.children:
      if func(child):
        result.append(self.find_result(depth, child))
    for child in self.children:
      result += child._find_children(func, depth + 1)
    return result

#  def has_child(self, data):
#    return self.caca_find_child(data) != None

  def ensure_path(self, path):
    current_node = self
    for next in path:
      current_node = current_node.ensure_child(next)
  
  def to_string(self, depth, indent = 2):
    buf = StringIO.StringIO()
    buf.write(' ' * depth)
    buf.write(str(self.data))
    buf.write('\n')
    for child in self.children:
      buf.write(child.to_string(depth + indent))
    return buf.getvalue()
