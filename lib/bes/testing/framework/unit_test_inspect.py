#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import ast, os.path as path
from bes.fs import file_util
from bes.system import compat
from .unit_test_description import unit_test_description

class unit_test_inspect(object):

  @classmethod
  def inspect_file(clazz, filename):
    code = file_util.read(filename)
    tree = ast.parse(code, filename = filename)
    s = ast.dump(tree, annotate_fields = True, include_attributes = True)
    result = []
    for node in tree.body:
      if clazz._node_is_unit_test_class(node):
        for statement in node.body:
          if isinstance(statement, ast.FunctionDef):
            if statement.name.startswith('test_'):
              result.append(unit_test_description(filename, node.name, statement.name))
    return result

  @classmethod
  def _node_is_unit_test_class(clazz, node):
    if not isinstance(node, ast.ClassDef):
      return False
    for i, base in enumerate(node.bases):
      base_class_name = clazz._base_class_name(base)
      if base_class_name in [ 'unittest.TestCase', 'unit_test', 'script_unit_test' ]:
        return True
    return False
    
  @classmethod
  def _base_class_name(clazz, base):
    result = []
    for field in base._fields:
      value = getattr(base, field)
      if isinstance(value, ast.Name):
        result.append(value.id)
      elif compat.is_string(value):
        result.append(value)
    return '.'.join(result)
    
  @classmethod
  def inspect_map(clazz, files):
    result = {}
    for f in files:
      f_path = path.abspath(f)
      try:
        tests = clazz.inspect_file(f_path)
        if tests:
          result[f_path] = clazz.inspect_file(f_path)
      except SyntaxError as ex:
        #printer.writeln('Failed to inspect: %s - %s' % (f, str(ex)))
        print('Failed to inspect: %s - %s' % (f, str(ex)))
        raise
      except Exception as ex:
        #printer.writeln('Failed to inspect: %s - %s:%s' % (f, type(ex), str(ex)))
        print('Failed to inspect: %s - %s:%s' % (f, type(ex), str(ex)))
    return result
