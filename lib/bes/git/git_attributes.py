#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from ..system.check import check
from bes.common.type_checked_list import type_checked_list
from bes.text.line_break import line_break
from bes.text.text_line_parser import text_line_parser

from .git_attributes_item import git_attributes_item

class git_attributes(type_checked_list):

  __value_type__ = git_attributes_item
  
  def __init__(self, values = None):
    super(git_attributes, self).__init__(values = values)

  def __str__(self):
    return self.to_string(delimiter = line_break.DEFAULT_LINE_BREAK) + line_break.DEFAULT_LINE_BREAK

  @classmethod
  def parse(clazz, text):
    check.check_string(text)

    lines = text_line_parser.parse_lines(text, strip_comments = False, strip_text = True, remove_empties = True)
    return git_attributes([ git_attributes_item.parse(line) for line in lines ])
  
  def sort(self, reverse = False):
    return self.sort(key = lambda item: item.pattern, reverse = reverse)
    
  def to_dict(self, short_hash = False):
    result = {}
    for item in self:
      if item.pattern in result:
        raise ValueError('duplicate pattern: "{}"'.format(item.pattern))
      result[item.pattern] = item
    return result

  def to_json(self, short_hash = False):
    d = self.to_dict(short_hash = short_hash)
    return json_util.to_json(d, indent = 2, sort_keys = True)
  
  def output(self, output_filename = None):
    check.check_string(output_filename, allow_none = True)
    
    with file_util.open_with_default(filename = output_filename) as fout:
        fout.write(self.to_json(short_hash = True))
        fout.write(line_break.DEFAULT_LINE_BREAK)
        
check.register_class(git_attributes, include_seq = False)
