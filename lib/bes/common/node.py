#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple
from bes.compat import StringIO

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
    return self.find_child_by_data(data, recurse = False) or self.add_child(data)

  def num_children(self):
    return len(self.children)

  def find_child_by_data(self, data, recurse = True):
    func = lambda node: node.data == data
    return self.find_child(func, recurse = recurse)
  
  find_result = namedtuple('find_result', 'depth,child')

  def find_children(self, func, recurse = True):
    return self._find_children(func, 0, recurse)

  def find_child(self, func, recurse = True):
    found = self._find_children(func, 0, recurse)
    if not found:
      return None
    return found[0].child

  def _find_children(self, func, depth, recurse):
    result = []
    for child in self.children:
      if func(child):
        result.append(self.find_result(depth, child))
    if recurse:
      for child in self.children:
        result += child._find_children(func, depth + 1, recurse)
    return result

  def ensure_path(self, path):
    current_node = self
    for next in path:
      current_node = current_node.ensure_child(next)
  
  def to_string(self, depth = 0, indent = 2, data_func = None):
    buf = StringIO()
    buf.write(' ' * depth)
    if data_func:
      data_str = data_func(self.data)
    else:
      data_str = str(self.data)
    buf.write(data_str)
    buf.write('\n')
    for child in self.children:
      buf.write(child.to_string(depth + indent, data_func = data_func))
    return buf.getvalue()

  flat_result = namedtuple('flat_result', 'path, node')
      
  @classmethod
  def _flatten(clazz, result, stack, n):
    stack.append(n)
    if not n.children:
      p = '/'.join([ n.data for n in stack])
      result.append(clazz.flat_result(p, n))
      stack.pop()
    else:
      for child in n.children:
        clazz._flatten(result, stack, child)
      stack.pop()

  def flat_paths(self):
    'Return a list of ( path, node ) tuples for all leaf nodes.'
    stack = []
    result = []
    self._flatten(result, stack, self)
    return sorted(result, key = lambda x: ( x.path.count('/'), x.path ))
