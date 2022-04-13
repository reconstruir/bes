# -*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import re

from collections import namedtuple

from ..system.check import check
from bes.common.string_util import string_util
from bes.property.cached_property import cached_property
from bes.system.log import logger
from bes.text.text_line_parser import text_line_parser

from .git_error import git_error
from .git_exe import git_exe
from .git_commit_hash import git_commit_hash

class git_ref_info(namedtuple('git_ref_info', 'name, full_name, ref_type, commit, commit_short, has_remote')):
  '''
  A class to hold information about a ref.
  Note: In git you can have a tag with the same name as a branch which seems
  like asking for trouble.  This class simplifies things and treats that case as an error.
  '''

  REF_TYPE_BRANCH = 'branch'
  REF_TYPE_TAG = 'tag'

  VALID_REF_TYPES = ( REF_TYPE_BRANCH, REF_TYPE_TAG )

  log = logger('git')
  
  def __new__(clazz, name, full_name, ref_type, commit, commit_short, has_remote):
    check.check_string(name)
    check.check_string(full_name)
    check.check_string(ref_type)
    check.check_string(commit)
    check.check_string(commit_short)
    check.check_bool(has_remote, allow_none = True)

    if ref_type not in clazz.VALID_REF_TYPES:
      raise git_error('Invalid ref_type: {}'.format(ref_type))
    
    return clazz.__bases__[0].__new__(clazz, name, full_name, ref_type, commit, commit_short, has_remote)

  def __str__(self):
    values = dict(self._asdict())
    if self.ref_type == self.REF_TYPE_BRANCH:
      return '{ref_type}:{name}:{commit_short}:{has_remote}'.format(**values)
    elif self.ref_type == self.REF_TYPE_TAG:
      return '{ref_type}:{name}:{commit_short}'.format(**values)
    else:
      assert False

  @cached_property
  def is_tag(self):
    'Return True if head is detached (tag or detached_commit)'
    return self.ref_type == self.REF_TYPE_TAG
        
  @cached_property
  def is_branch(self):
    'Return True if head points to a branch'
    return self.ref_type == self.REF_TYPE_BRANCH

  @classmethod
  def parse_show_ref_output(clazz, text):
    check.check_string(text)

    lines = text_line_parser.parse_lines(text, strip_comments = False, strip_text = True, remove_empties = True)
    items = [ clazz._parse_line(line) for line in lines ]
    head_item = next(iter([ item for item in items if item.full_name.startswith('refs/heads') ]), None)
    remote_item = next(iter([ item for item in items if item.full_name.startswith('refs/remotes') ]), None)
    tag_item = next(iter([ item for item in items if item.full_name.startswith('refs/tags') ]), None)

    clazz.log.log_d('       text: {}'.format(text))
    clazz.log.log_d('      lines: {}'.format(lines))
    clazz.log.log_d('  head_item: {}'.format(head_item))
    clazz.log.log_d('remote_item: {}'.format(remote_item))
    clazz.log.log_d('   tag_item: {}'.format(tag_item))
    
    if tag_item and (head_item or remote_item):
      raise git_error('Ref that is both a branch and tag is not supported: {}'.format(tag_item.full_name))

    if tag_item:
      ref_type = clazz.REF_TYPE_TAG
      commit = tag_item.commit
      full_name = tag_item.full_name
      has_remote = False
    else:
      ref_type = clazz.REF_TYPE_BRANCH
      if head_item:
        commit = head_item.commit
        full_name = head_item.full_name
        has_remote = remote_item != None
      elif remote_item:
        commit = remote_item.commit
        full_name = remote_item.full_name
        has_remote = True
      else:
        raise git_error('Failed to determine ref type: {}'.format(text))

    name = full_name.split('/')[-1]
    commit_short = git_commit_hash.shorten(commit)
    return git_ref_info(name, full_name, ref_type, commit, commit_short, has_remote)
                                      
  _show_ref_item = namedtuple('_show_ref_item', 'commit, full_name')
  @classmethod
  def _parse_line(clazz, line):
    parts = string_util.split_by_white_space(line, strip = True)
    if len(parts) != 2:
      raise git_error('Invalid show-ref line: "{}"'.format(line))
    commit_long = parts[0]
    fullname = parts[1]
    return clazz._show_ref_item(commit_long, fullname)
