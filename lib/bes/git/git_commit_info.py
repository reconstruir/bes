# -*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import re

from ..system.check import check
from bes.property.cached_property import cached_property

from .git_commit_hash import git_commit_hash

class git_commit_info(object):
  'Class to hold information about one git commit.'
  
  def __init__(self, commit_hash_long, message, author = None, email = None, date = None, is_merge_commit = False):
    check.check_string(commit_hash_long, allow_none = True)
    check.check_string(message, allow_none = True)
    check.check_string(author, allow_none = True)
    check.check_string(email, allow_none = True)
    check.check_string(date, allow_none = True)

    self.commit_hash_long = commit_hash_long
    self.message = message
    self.author = author
    self.email = email
    self.date = date
    self.is_merge_commit = is_merge_commit

  @cached_property
  def commit_hash_short(self):
    return git_commit_hash.shorten(self.commit_hash_long)
    
  def __str__(self):
    parts = [
      self.commit_hash_long,
      self.date,
      self.author or self.email,
      self.message,
    ]
    parts = [ part for part in parts if part ]
    return ' '.join(parts)

  def __repr__(self):
    return str(self)
  
  def __len__(self):
    return len(str(self))

  @classmethod
  def parse_log_output(clazz, text):
    'Parse the output of git log for one commit'
    commit_parts = [ elem.strip() for elem in text.splitlines() if elem ]
    revision = commit_parts[0].split('commit ')[-1]
    revision = re.search(r'(\w+)\s*.*', revision).group(1)
    index = 1
    is_merge_commit = False
    if commit_parts[1].startswith('Merge: '):
      index += 1
      is_merge_commit = True
    email = re.search(r'Author: .*\s+<(.+)>', commit_parts[index]).group(1)
    author = email.split('@')[0]
    date = re.search(r'Date:\s+(.+)', commit_parts[index + 1]).group(1)
    message = ' '.join(commit_parts[index + 2:]).strip()
    return git_commit_info(revision, message, author, email, date, is_merge_commit)

check.register_class(git_commit_info, include_seq = True)
  
