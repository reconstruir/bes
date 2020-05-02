# -*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import re

from collections import namedtuple

from bes.text.text_line_parser import text_line_parser

from .git_error import git_error

class git_head_info(object):
  'A class to deal with git head info.'

  _head_info = namedtuple('_head_info', 'branch, ref, commit_hash, commit_message, is_detached')
  @classmethod
  def parse_head_info(clazz, text):
    lines = text_line_parser.parse_lines(text, strip_comments = False, strip_text = True, remove_empties = True)
    active_line = clazz._find_active_branch_entry(lines)
    if not active_line:
      raise git_error('Failed to get head info')
    detached_info = clazz._parse_detached_head_line(active_line)
    if detached_info:
      ref = detached_info[0]
      commit_hash = detached_info[1]
      commit_message = detached_info[2]
      return clazz._head_info(None, ref, commit_hash, commit_message, True)
    info = clazz._parse_head_line(active_line)
    if not info:
      raise git_error('Failed to parse head info: "{}"'.format(active_line))
    branch = info[0].strip()
    commit_hash = info[1]
    commit_message = info[2]
    return clazz._head_info(branch, None, commit_hash, commit_message, False)

  @classmethod
  def _find_active_branch_entry(clazz, lines):
    for line in lines:
      if line.startswith('*'):
        return line
    return none

  _DETACHED_HEAD_PATTERN = r'^\*\s+\(HEAD\s+detached\s+at\s+(.+)\)\s+([0-9a-f]+)\s+(.+)$'
  @classmethod
  def _parse_detached_head_line(clazz, line):
    f = re.findall(clazz._DETACHED_HEAD_PATTERN, line)
    if not f:
      return None
    assert len(f) == 1
    assert len(f[0]) == 3
    return f[0]

  _HEAD_PATTERN = r'^\*\s+(.+)\s+([0-9a-f]+)\s+(.+)$'
  @classmethod
  def _parse_head_line(clazz, line):
    f = re.findall(clazz._HEAD_PATTERN, line)
    if not f:
      return None
    assert len(f) == 1
    assert len(f[0]) == 3
    return f[0]

