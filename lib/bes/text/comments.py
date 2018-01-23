#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

class comments(object):

  @classmethod
  def strip_line(clazz, s, strip_head = False, strip_tail = False):
    'Strip comments from one line.'
    i = s.find('#')
    if i >= 0:
      result = s[0:i]
    else:
      result = s
    if strip_head and strip_tail:
      result = result.strip()
    elif strip_head:
      result = result.lstrip()
    elif strip_tail:
      result = result.rstrip()
    return result

  @classmethod
  def strip_multi_line(clazz, s, strip_head = False, strip_tail = False, remove_empties = False):
    'Strip comments from multiple lines.'
    lines = s.split('\n')
    stripped_lines = [ clazz.strip_line(line, strip_head = strip_head, strip_tail = strip_tail) for line in lines ]
    if remove_empties:
      stripped_lines = [ line for line in stripped_lines if line ]
    return '\n'.join(stripped_lines)
