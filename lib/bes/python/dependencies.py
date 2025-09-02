#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path, re
from bes.system.which import which
from bes.system.execute import execute
from bes.text.text_line_parser import text_line_parser

class dependencies(object):
  'Class to deal with python dependencies.'

  @classmethod
  def is_supported(clazz):
    'Return True if this environment supports figuring out python file dependencies.'
    return which.which('sfood') is not None
  
  @classmethod
  def dependencies(clazz, filename):
    'Return list of files filename depends on or None if snakefood is not found.'
    try:
      sfood_exe = which.which('sfood')
    except RuntimeError as ex:
      return None
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

  _IMPORT_PATTERN = re.compile(r'^\s*import\s+(.+)\s+#\s+(from|precompiled\s+from)\s(.+)\s*$')
  
  @classmethod
  def caca_dependencies(clazz, filename, python_exe):
    'Return list of files filename depends on or None if snakefood is not found.'
    rv = execute.execute('%s -v %s' % (python_exe, filename), raise_error = False)
    parser = text_line_parser(rv.stderr)
    parser.remove_empties()
    for line in parser:
      f = clazz._IMPORT_PATTERN.findall(line.text)
      if f:
        print(f[0][2])
    return None
