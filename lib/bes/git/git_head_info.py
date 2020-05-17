# -*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import re

from collections import namedtuple

from bes.common.check import check
from bes.common.string_util import string_util
from bes.text.text_line_parser import text_line_parser

from .git_error import git_error
from .git_exe import git_exe

class git_head_info(namedtuple('git_head_info', 'state, branch, ref, commit_hash, commit_message, ref_branches')):
  'A class to deal with git head info.'

  STATE_BRANCH = 'branch'
  STATE_DETACHED_COMMIT = 'detached_commit'
  STATE_TAG = 'tag'
  
  STATES = ( STATE_BRANCH, STATE_DETACHED_COMMIT, STATE_TAG )
  
  def __new__(clazz, state, branch, ref, commit_hash, commit_message, ref_branches):
    check.check_string(state)
    check.check(branch, (check.STRING_TYPES, list ), allow_none = True)
    check.check_string(ref, allow_none = True)
    check.check_string(commit_hash)
    check.check_string(commit_message)
    check.check_string_seq(ref_branches, allow_none = True)

    if state not in clazz.STATES:
      raise git_error('Invalid state: "{}"'.format(state))
    return clazz.__bases__[0].__new__(clazz, state, branch, ref, commit_hash, commit_message, ref_branches)

  def __str__(self):
    values = dict(self._asdict())
    if self.state == self.STATE_BRANCH:
      return 'branch:{branch}:{commit_hash}'.format(**values)
    elif self.state == self.STATE_TAG:
      return 'tag:{ref}:{commit_hash}'.format(**values)
    elif self.state == self.STATE_DETACHED_COMMIT:
      return 'detached_commit::{commit_hash}'.format(**values)
    else:
      assert False

  @property
  def is_detached(self):
    'Return True if head is detached (tag or detached_commit)'
    return self.state in ( self.STATE_TAG, self.STATE_DETACHED_COMMIT )
        
  @property
  def is_branch(self):
    'Return True if head points to a branch'
    return self.state == self.STATE_BRANCH
    
  @property
  def is_detached_commit(self):
    'Return True if head points to a detached commit'
    return self.state == self.STATE_DETACHED_COMMIT
    
  @property
  def is_tag(self):
    'Return True if head points to a tag'
    return self.state == self.STATE_TAG

  @classmethod
  def parse_head_info(clazz, root, text):
    check.check_string(root, allow_none = True)
    check.check_string(text)

    lines = text_line_parser.parse_lines(text, strip_comments = False, strip_text = True, remove_empties = True)
    active_line = clazz._find_active_branch_entry(lines)
    if not active_line:
      raise git_error('Failed to get head info')
    detached_info = clazz._parse_detached_head_line(active_line)
    if detached_info:
      ref = detached_info[0]
      assert ref
      commit_hash = detached_info[1]
      assert commit_hash
      commit_message = detached_info[2]
      assert commit_message
      if root:
        ref_branches = clazz._branches_for_ref(root, ref)
      else:
        ref_branches = None
      if ref != commit_hash:
        state = clazz.STATE_TAG
      else:
        state = clazz.STATE_DETACHED_COMMIT
      return git_head_info(state, None, ref, commit_hash, commit_message, ref_branches)
#branch, commit_hash, commit_message
    info = clazz._parse_active_branch_entry(active_line)
    print('info={}'.format(info))
    if not info:
      raise git_error('Failed to parse head info: "{}"'.format(active_line))
    branch = info[0].strip()
    assert branch
    commit_hash = info[1]
    assert commit_hash
    commit_message = info[2]
    assert commit_message
    return git_head_info(clazz.STATE_BRANCH, branch, None, commit_hash, commit_message, None)

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

  @classmethod
  def _parse_active_branch_entry(clazz, entry):
    parts = string_util.split_by_white_space(entry, strip = True)
    if len(parts) < 4:
      raise git_error('Invalid active branch entry: "{}"'.format(entry))
    if parts[0] != '*':
      raise git_error('Invalid active branch entry: "{}"'.format(entry))

    branch = parts[1]
    commit_hash = parts[2]
    commit_message = entry[entry.find(commit_hash) + len(commit_hash) + 1:]
    return ( branch, commit_hash, commit_message )

  @classmethod
  def _branches_for_ref(clazz, root, ref):
    cmd = [ 'branch', '--contains', ref ]
    rv = git_exe.call_git(root, cmd, raise_error = False)
    if rv.exit_code != 0:
      return None
    result = []
    lines = git_exe.parse_lines(rv.stdout)
    for line in lines:
      branch_ref = 'refs/heads/{}'.format(line)
      cmd = [ 'show-ref', '--verify', branch_ref ]
      rv = git_exe.call_git(root, [ 'show-ref', '--verify', '--quiet', branch_ref ], raise_error = False)
      if rv.exit_code == 0:
        result.append(line)
    return sorted(result)
