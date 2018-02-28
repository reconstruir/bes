#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path, sys

class printer(object):
  
  OUTPUT = sys.stdout
  NAME = path.basename(sys.argv[0])
  
  @classmethod
  def writeln(clazz, s):
    clazz.write(s)
    clazz.write('\n')
    clazz.flush()
          
  @classmethod
  def writeln_name(clazz, s):
    clazz.write(clazz.NAME)
    clazz.write(': ')
    clazz.write(s)
    clazz.write('\n')
    clazz.flush()
          
  @classmethod
  def write(clazz, s, flush = False):
    clazz.OUTPUT.write(s)
    if flush:
      clazz.flush()
          
  @classmethod
  def flush(clazz):
    clazz.OUTPUT.flush()
