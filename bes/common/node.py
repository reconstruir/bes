#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

class node(object):

  def __init__(self, data):
    self.data = data
    self.children = []

  def __eq__(self, other):
    return self.__dict__ == other.__dict__

  def add_child(self, data):
    self.children.append(node(data))

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
    pass
