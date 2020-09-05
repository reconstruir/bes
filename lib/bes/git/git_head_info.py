# -*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import re

from collections import namedtuple

from bes.common.check import check
from bes.common.string_util import string_util
from bes.fs.file_match import file_match
from bes.system.log import logger
from bes.text.text_line_parser import text_line_parser

from .git_error import git_error
from .git_ref import git_ref

class git_head_info(namedtuple('git_head_info', 'state, branch, ref, commit_hash, commit_message, ref_branches')):
  'A class to deal with git head info.'

  STATE_BRANCH = 'branch'
  STATE_DETACHED_COMMIT = 'detached_commit'
  STATE_NOTHING = 'nothing'
  STATE_TAG = 'tag'
  
  STATES = ( STATE_BRANCH, STATE_DETACHED_COMMIT, STATE_NOTHING, STATE_TAG )

  log = logger('git')
  
  def __new__(clazz, state, branch, ref, commit_hash, commit_message, ref_branches):
    check.check_string(state)
    check.check(branch, (check.STRING_TYPES, list ), allow_none = True)
    check.check_string(ref, allow_none = True)
    check.check_string(commit_hash, allow_none = True)
    check.check_string(commit_message, allow_none = True)
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
    elif self.state == self.STATE_NOTHING:
      return 'nothing::'
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
  def parse_head_info(clazz, root_dir, text):
    check.check_string(root_dir, allow_none = True)
    check.check_string(text)

    clazz.log.log_d('parse_head_info: text={}'.format(text))
    
    if text == '':
      return git_head_info(clazz.STATE_NOTHING, None, None, None, None, None)
    
    lines = text_line_parser.parse_lines(text, strip_comments = False, strip_text = True, remove_empties = True)
    clazz.log.log_d('parse_head_info: lines={}'.format(lines))
    active_line = clazz._find_active_branch_entry(lines)
    if not active_line:
      raise git_error('Failed to get head info')
    detached_info = clazz._parse_detached_head_line(active_line)
    clazz.log.log_d('parse_head_info: detached_info={}'.format(detached_info))
    
    if detached_info:
      if root_dir:
        ref_branches = git_ref.branches_for_ref(root_dir, detached_info.commit)
      else:
        ref_branches = None
      if detached_info.ref != detached_info.commit:
        state = clazz.STATE_TAG
        ref = detached_info.ref
      else:
        state = clazz.STATE_DETACHED_COMMIT
        ref = None
      return git_head_info(state,
                           None,
                           ref,
                           detached_info.commit,
                           detached_info.message,
                           ref_branches)
    info = clazz._parse_active_branch_entry(active_line)
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
    return None

  _DETACHED_HEAD_PATTERN = r'^\*\s+\(HEAD\s+detached\s+(at|from)\s+(.+)\)\s+([0-9a-f]+)\s+(.*)$'
  _detached_head_info = namedtuple('_detached_head_info', 'where, ref, commit, message')
  @classmethod
  def _parse_detached_head_line(clazz, line):
    f = re.findall(clazz._DETACHED_HEAD_PATTERN, line)
    if not f:
      return None
    assert len(f) == 1
    assert len(f[0]) == 4
    assert f[0][0] in ( 'at', 'from' )
    return clazz._detached_head_info(*f[0])

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

  def match_ref_branches(self, patterns):
    if not self.ref_branches:
      return None
    return file_match.match_fnmatch(self.ref_branches, patterns)

  def determine_unique_branch(self, patterns):
    if self.is_branch:
      return self.branch
    matches = self.match_ref_branches(patterns)
    if matches == None:
      return None
    if len(matches) == 1:
      return matches[0]
    return None
