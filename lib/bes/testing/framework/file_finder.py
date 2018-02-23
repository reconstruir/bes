#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import subprocess
from bes.text import lines
from bes.fs import file_find

class file_finder(object):

  @classmethod
  def find_python_files(clazz, d):
    return file_find.find_fnmatch(d, [ '*.py' ], relative = False)

  @classmethod
  def find_tests(clazz, d):
    return file_find.find_fnmatch(d, [ '*test_*.py' ], relative = False)
