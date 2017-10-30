#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

class code(object):
  'Class to deal with python code.'

  @classmethod
  def execfile(clazz, filename, xglobals, xlocals):
    try:      
      with open(filename, 'r') as f:
        content = f.read()
    except Exeption as ex:
      raise
    c = compile(content, filename, 'exec')
    exec(c, xglobals, xlocals)
