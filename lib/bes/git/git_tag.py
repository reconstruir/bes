#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import re
from collections import namedtuple

from bes.common.check import check
from bes.common.string_util import string_util
from bes.common.type_checked_list import type_checked_list
from bes.common.json_util import json_util
from bes.text.text_line_parser import text_line_parser
from bes.version.software_version import software_version
from bes.fs.file_util import file_util
from bes.text.text_table import text_table
from bes.common.table import table

from .git_commit_hash import git_commit_hash
from .git_error import git_error
from .git_output_style import git_output_style

class git_tag(namedtuple('git_tag', 'name, commit, commit_short, peeled')):

  def __new__(clazz, name, commit, commit_short, peeled):
    return clazz.__bases__[0].__new__(clazz, name, commit, commit_short, peeled)

  def to_dict(self):
    return dict(self._asdict())
  
  SORT_TYPES = ( 'lexical', 'version' )
  @classmethod
  def parse_show_ref_output(clazz, s, sort_type = 'version', reverse = False):
    check.check_string(s)
    check.check_string(sort_type)
    check.check_bool(reverse)
    
    if sort_type not in clazz.SORT_TYPES:
      raise git_error('invalid sort_type: "{}"'.format(sort_type))
    
    lines = text_line_parser.parse_lines(s,
                                         strip_comments = False,
                                         strip_text = True,
                                         remove_empties = True)
    if not lines:
      return []
    tags = git_tag_list([ clazz._parse_show_ref_one_line(line) for line in lines ])
    if sort_type == 'lexical':
      tags.sort_lexical(reverse = reverse)
    elif sort_type == 'version':
      tags.sort_version(reverse = reverse)
    return tags

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
  
check.register_class(git_tag_list, include_seq = False)
  