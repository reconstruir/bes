#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

class comments(object):

  @classmethod
  def strip_line(clazz, s, strip = False):
    'Strip comments from one line.'
    i = s.find('#')
    if i >= 0:
      result = s[0:i]
    else:
      result = s
    if strip:
      result = result.strip()
    return result

  @classmethod
  def strip_multi_line(clazz, s, strip = False, remove_empties = False):
    'Strip comments from multiple lines.'
    lines = s.split('\n')
    stripped_lines = [ clazz.strip_line(line, strip = strip) for line in lines ]
    if remove_empties:
      stripped_lines = [ line for line in stripped_lines if line ]
    return '\n'.join(stripped_lines)
