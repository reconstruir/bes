#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

# A script to run python unit tests.  Does not use any bes code to avoid
# chicken-and-egg issues and to be standalone
import argparse, ast, copy, fnmatch, math, os, os.path as path, platform, random, re, subprocess, sys
import exceptions, glob, shutil, time, tempfile
from collections import namedtuple

from bes.testing.framework import argument_resolver, config_file_caca, file_filter
from bes.common import algorithm, object_util, string_util
from bes.git import git
from bes.text import comments, lines
from bes.fs import file_find, file_path, file_util
from bes.dependency import dependency_resolver
from bes.egg import egg

class unit_test_inspect(object):
  unit_test = namedtuple('unit_test', 'filename,fixture,function')

  @classmethod
  def inspect_file(clazz, filename):
    code = file_util.read(filename)
    if 'bes:skip_unit_test=1' in code:
      return []
    tree = ast.parse(code, filename = filename)
    s = ast.dump(tree, annotate_fields = True, include_attributes = True)
    result = []
    for node in tree.body:
      if clazz._node_is_unit_test_class(node):
        for statement in node.body:
          if isinstance(statement, ast.FunctionDef):
            if statement.name.startswith('test_'):
              result.append(clazz.unit_test(filename, node.name, statement.name))
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
      elif isinstance(value, ( str, unicode)):
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
      except exceptions.SyntaxError, ex:
        printer.writeln('Failed to inspect: %s - %s' % (f, str(ex)))
        raise
      except Exception, ex:
        printer.writeln('Failed to inspect: %s - %s:%s' % (f, type(ex), str(ex)))
    return result

  @classmethod
  def print_inspect_map(clazz, inspect_map, files, cwd):
    for filename in sorted(inspect_map.keys()):
      if filename in files:
        printer.writeln('%s:' % (file_util.remove_head(filename, cwd)))
        for _, fixture, function in inspect_map[filename]:
          printer.writeln('  %s.%s' % (fixture, function))
