#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from ..system.check import check
from ..property.cached_property import cached_property

from collections import defaultdict

class _bcli_parser_tree_node:
  
  def __init__(self):
    self.children = defaultdict(_bcli_parser_tree_node)
    self.value = None

class bcli_parser_tree:
  def __init__(self):
    self.root = _bcli_parser_tree_node()

  def ensure_path(self, path):
    '''Ensure that the given path exists, and return the final node.'''
    check.check_string_seq(path)
    
    node = self.root
    for part in path:
      node = node.children[part]
    return node

  def set(self, path, value):
    '''Set a value at the path. Raise if value already exists there.'''
    check.check_string_seq(path)

    node = self.ensure_path(path)
    if node.value is not None:
      raise ValueError(f"Path {'/'.join(path)} already has a value.")
    node.value = value

  def get(self, path):
    '''Return the node at the given path, or None if it doesn't exist.'''
    check.check_string_seq(path)

    node = self.root
    for part in path:
      if part not in node.children:
        return None
      node = node.children[part]
    return node

  def get_value(self, path):
    '''Return the value at the given path, or None if missing.'''
    check.check_string_seq(path)

    node = self.get(path)
    return node.value if node else None

  def get_safe(self, path):
    '''Return (actual_path, node) for the given path. Raise if any part is missing.'''
    check.check_string_seq(path)

    node = self.root
    actual_path = []

    for part in path:
      if part not in node.children:
        raise KeyError(f"Path not found: {'/'.join(actual_path + [part])}")
      node = node.children[part]
      actual_path.append(part)

    return (actual_path, node)

  def get_existing_prefix(self, path):
    '''Return (matched_path, node) for the deepest existing part of the path.'''
    check.check_string_seq(path)

    node = self.root
    actual_path = []

    for part in path:
      if part not in node.children:
        break
      node = node.children[part]
      actual_path.append(part)

    return (actual_path, node if actual_path else None)
  
  def __repr__(self):
    def repr_node(node, indent=0):
      lines = []
      for key, child in node.children.items():
        value_part = f" = {child.value}" if child.value is not None else ""
        lines.append("  " * indent + f"{key}{value_part}")
        lines.extend(repr_node(child, indent + 1))
      return lines
    return "\n".join(repr_node(self.root))
