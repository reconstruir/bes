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
    self._root = _bcli_parser_tree_node()

  def ensure_path(self, path):
    '''Ensure that the given path exists, and return the final node.'''
    check.check_string_seq(path)
    
    node = self._root
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

    node = self._root
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

    node = self._root
    actual_path = []

    for part in path:
      if part not in node.children:
        raise KeyError(f"Path not found: {'/'.join(actual_path + [part])}")
      node = node.children[part]
      actual_path.append(part)

    return (actual_path, node)

  def get_existing_prefix(self, path):
    '''Return (matched_path, node, leftover_path) for the deepest existing part of the path.'''
    check.check_string_seq(path)
  
    node = self._root
    actual_path = []
  
    for i, part in enumerate(path):
      if part not in node.children:
        return actual_path, node if actual_path else None, path[i:]
      node = node.children[part]
      actual_path.append(part)
  
    return actual_path, node, []

  def resolve_token(self, token, candidates):
    '''Resolve a token against candidates using matching heuristics.'''
    # 1. Exact
    if token in candidates:
      return token
  
    # 2. Prefix
    prefix_matches = [c for c in candidates if c.startswith(token)]
    if len(prefix_matches) == 1:
      return prefix_matches[0]
    if len(prefix_matches) > 1:
      raise ValueError(
        f"Ambiguous token '{token}' matches multiple options by prefix: {sorted(prefix_matches)}"
      )
  
    # 3. First-last letters
    first_last_matches = [c for c in candidates if len(c) >= 2 and (c[0] + c[-1]) == token]
    if len(first_last_matches) == 1:
      return first_last_matches[0]
    if len(first_last_matches) > 1:
      raise ValueError(
        f"Ambiguous token '{token}' matches multiple options by first-last letters: {sorted(first_last_matches)}"
      )
  
    # 4. Dash-initials
    dash_initials_matches = []
    for c in candidates:
      parts = c.split('-')
      initials = ''.join(p[0] for p in parts if p)
      if initials == token:
        dash_initials_matches.append(c)
    if len(dash_initials_matches) == 1:
      return dash_initials_matches[0]
    if len(dash_initials_matches) > 1:
      raise ValueError(
        f"Ambiguous token '{token}' matches multiple options by dash initials: {sorted(dash_initials_matches)}"
      )

    # 5. underscore
    dash_initials_matches = []
    for c in candidates:
      parts = c.split('_')
      initials = ''.join(p[0] for p in parts if p)
      if initials == token:
        dash_initials_matches.append(c)
    if len(dash_initials_matches) == 1:
      return dash_initials_matches[0]
    if len(dash_initials_matches) > 1:
      raise ValueError(
        f"Ambiguous token '{token}' matches multiple options by dash initials: {sorted(dash_initials_matches)}"
      )
    
    # Nothing matched
    raise KeyError(f"Unrecognized token '{token}' among options: {sorted(candidates)}")
  
  def get_safe_with_shortcuts(self, path):
    '''
    Resolve path with shortcuts.
    Return (actual_path, node).
    Raises if any part cannot be resolved.
    '''
    check.check_string_seq(path)
    
    node = self._root
    actual_path = []
    
    for part in path:
      candidates = node.children.keys()
      if not candidates:
        raise KeyError(f"No subcommands under: {'/'.join(actual_path)}")
      
      resolved = self.resolve_token(part, candidates)
      node = node.children[resolved]
      actual_path.append(resolved)
    
    return (actual_path, node)
  
  def __repr__(self):
    def repr_node(node, indent=0):
      lines = []
      for key, child in node.children.items():
        value_part = f" = {child.value}" if child.value is not None else ""
        lines.append("  " * indent + f"{key}{value_part}")
        lines.extend(repr_node(child, indent + 1))
      return lines
    return "\n".join(repr_node(self._root))

  def format_help(self):
    def _help_node(node, indent=0):
      lines = []
      for key, child in node.children.items():
        value_part = f" - {child.value.description()}" if child.value is not None else ""
        lines.append("  " * indent + f"{key}{value_part}")
        lines.extend(_help_node(child, indent + 1))
      return lines
    return "\n".join(_help_node(self._root))
  
