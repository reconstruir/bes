#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import re
from collections import namedtuple

from bes.common.algorithm import algorithm
from bes.common.check import check
from bes.common.json_util import json_util
from bes.common.string_util import string_util
from bes.common.table import table
from bes.common.type_checked_list import type_checked_list
from bes.fs.file_util import file_util
from bes.text.text_line_parser import text_line_parser
from bes.text.text_table import text_table
from bes.version.software_version import software_version

from .git_commit_hash import git_commit_hash
from .git_error import git_error
from .git_output_style import git_output_style
from .git_tag_sort_type import git_tag_sort_type

class git_tag(namedtuple('git_tag', 'name, commit, commit_short, peeled')):

  def __new__(clazz, name, commit, commit_short, peeled):
    return clazz.__bases__[0].__new__(clazz, name, commit, commit_short, peeled)

  def to_dict(self):
    return dict(self._asdict())
  
  @classmethod
  def parse_show_ref_output(clazz, s, sort_type = None, reverse = False,
                            limit = None, prefix = None):
    check.check_string(s)
    sort_type = git_tag_sort_type.check_sort_type(sort_type)
    check.check_bool(reverse)
    check.check_int(limit, allow_none = True)
    check.check_string(prefix, allow_none = True)
    
    lines = text_line_parser.parse_lines(s,
                                         strip_comments = False,
                                         strip_text = True,
                                         remove_empties = True)
    if not lines:
      return git_tag_list()
    parsed_tags = [ clazz._parse_show_ref_one_line(line) for line in lines ]
    tags = git_tag_list(parsed_tags)
    if sort_type == 'lexical':
      tags.sort_lexical(reverse = reverse)
    elif sort_type == 'version':
      tags.sort_version(reverse = reverse)
    if prefix:
      tags = tags.filter_by_prefix(prefix)
    if limit != None:
      tags = tags[0:limit]
    return tags

  @classmethod
  def _parse_show_ref_one_line(clazz, s):
    s = string_util.unquote(s)
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

check.register_class(git_tag, include_seq = False)

class git_tag_list(type_checked_list):

  __value_type__ = git_tag
  
  def __init__(self, values = None):
    super(git_tag_list, self).__init__(values = values)

  def sort_lexical(self, reverse = False):
    return self.sort(key = lambda tag: tag.name, reverse = reverse)
    
  def sort_version(self, reverse = False):
    return self.sort(key = lambda tag: software_version.parse_version(tag.name), reverse = reverse)

  def to_dict(self, short_hash = False):
    result = {}
    for tag in self:
      tag_dict = tag.to_dict()
      name = tag_dict['name']
      del tag_dict['name']
      if short_hash:
        tag_dict['commit'] = tag_dict['commit_short']
      del tag_dict['commit_short']
      result[name] = tag_dict
    return result

  def to_json(self, short_hash = False):
    d = self.to_dict(short_hash = short_hash)
    return json_util.to_json(d, indent = 2, sort_keys = True)
  
  def output(self, style, output_filename = None):
    git_output_style.check_style(style)

    with file_util.open_with_default(filename = output_filename) as fout:
      if style == 'brief':
        for tag in self:
          fout.write(tag.name)
          fout.write('\n')
      elif style == 'table':
        data = table(data = self._values)
        data.remove_column(3)
        data.remove_column(1)
        tt = text_table(data = data)
        tt.set_labels( ( 'TAG', 'COMMIT' ) )
        print(tt)
        pass
      elif style == 'json':
        fout.write(self.to_json(short_hash = True))
        fout.write('\n')

  def names(self):
    return algorithm.unique([ tag.name for tag in self ])

  def has_name(self, name):
    for tag in self:
      if tag.name == name:
        return True
    return False

  def filter_by_prefix(self, prefix):
    return git_tag_list([ tag for tag in self if tag.name.startswith(prefix) ])
        
check.register_class(git_tag_list, include_seq = False)
  
