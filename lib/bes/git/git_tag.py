#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import re
from collections import namedtuple

from bes.common.check import check
from bes.common.string_util import string_util
from bes.text.text_line_parser import text_line_parser
from bes.version.software_version import software_version

from .git_commit_hash import git_commit_hash

class git_tag(namedtuple('git_tag', 'name, commit, commit_short, peeled')):

  def __new__(clazz, name, commit, commit_short, peeled):
    return clazz.__bases__[0].__new__(clazz, name, commit, commit_short, peeled)

  @classmethod
  def parse_show_ref_output(clazz, s):
    lines = text_line_parser.parse_lines(s,
                                         strip_comments = False,
                                         strip_text = True,
                                         remove_empties = True)
    if not lines:
      return []
    tags = [ clazz._parse_show_ref_one_line(line) for line in lines ]
    return sorted(tags, key = lambda tag: software_version.parse_version(tag.name))

  @classmethod
  def _parse_show_ref_one_line(clazz, s):
    f = re.findall(r'^\s*([0-9a-f]{40})\s+refs/tags/(.+)\s*$', s)
    if not f:
      return None
    if len(f) != 1:
      return None
    commit = f[0][0]
    name = f[0][1]
    peeled = False
    if name.endswith('^{}'):
      name = string_util.remove_tail(name, '^{}')
      peeled = True
    return git_tag(name, commit, git_commit_hash.shorten(commit), peeled)

check.register_class(git_tag)
