#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import StringIO

class node(object):

  def __init__(self, data):
    self.data = data
    self.children = []

  def __eq__(self, other):
    return self.__dict__ == other.__dict__

  def __str__(self):
    return self.to_string(0)

  def add_child(self, data):
    n = node(data)
    self.children.append(n)
    return n

  def ensure_child(self, data):
    return self.find_child(data) or self.add_child(data)

  def num_children(self):
    return len(self.children)
    
  def find_child(self, data):
    for child in self.children:
      if child.data == data:
        return child
    return None

  def has_child(self, data):
    return self.find_child(data) != None

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
