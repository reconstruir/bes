#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from ..system.check import check
from bes.fs.file_util import file_util
from bes.text.text_line_parser import text_line_parser

class git_cli_util(object):

  @classmethod
  def read_tag_list_file(clazz, filename):
    'Read a list of tags from a file.  Each line should be one tag'
    check.check_string(filename)

    text = file_util.read(filename)
    lines = text_line_parser.parse_lines(text, remove_empties = True)
    result = []
    for i, line in enumerate(lines):
      if line:
        result.append(line)
    return sorted(result)
