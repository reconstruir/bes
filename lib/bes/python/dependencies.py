#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.fs import file_path
from bes.system import execute
from bes.text import text_line_parser

class dependencies(object):
  'Class to deal with python dependencies.'

  @classmethod
  def dependencies(clazz, filename):
    'Return list of files filename depends on.'
    sfood_exe = file_path.which('sfood')
    rv = execute.execute('%s %s' % (sfood_exe, filename))
    parser = text_line_parser(rv.stdout)
    parser.remove_empties()
    parser.append(',')
    code = '[ %s ]' % (str(parser))
    v = eval(code)
    result = []
    for item in v:
      p1, p2 = item[1] 
      if p1 and p2:
        filename = path.join(p1, p2)
        if path.isfile(filename):
          result.append(filename)
    return result
