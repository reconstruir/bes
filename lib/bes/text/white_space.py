#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

class white_space(object):
  'Deal with white spaces.'
      
  @classmethod
  def shorten_multi_line_spaces(self, text):
    lines = text.split('\n')
    for i, line in enumerate(lines):
      if line.isspace():
        lines[i] = ''
    return '\n'.join(lines)
