#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple
import os, os.path as path, re

from bes.fs import file_util
from bes.text.string_list import string_list
from bes.text.text_line_parser import text_line_parser

from .files import files

class import_expand(object):

  @classmethod
  def expand(clazz, namespace, dirs, sort, dry_run):
    assert isinstance(dirs, list)
    for d in dirs:
      clazz._expand_one_dir(namespace, d, sort, dry_run)

  @classmethod
  def _expand_one_dir(clazz, namespace, where, sort, dry_run):
    where = path.normpath(where)
    if '..' in where:
      raise RuntimeError('Invalid path - dont use \"..\" : %s' % (where))
    abs_where = path.abspath(where)
    py_files = files.find_python_files(abs_where)
    for filename in py_files:
      clazz._expand_one_file(namespace, filename, sort, dry_run)

  @classmethod
  def expand_text(clazz, namespace, text, sort):
    pattern = r'^\s*from\s+{}\.(.+)\s+import\s+(.+)\s*$'.format(namespace)
    lines = text_line_parser(text)
    mi_imports = clazz._parse_multi_imports(pattern, lines)
    if not mi_imports:
      return text
    # Reverse the line numbers so we work to expand imports backwards in
    # order not to mess the order of things in the content
    line_numbers = [ n for n in reversed(mi_imports.keys()) ]
    indeces = lines.indeces(line_numbers)

    for line_number in line_numbers:
      mi = mi_imports[line_number]
      texts = clazz._make_texts(namespace, mi, sort)
      lines.replace_line_with_lines(line_number, texts)

    return str(lines).rstrip() + '\n'

  @classmethod
  def _make_texts(clazz, namespace, mi, sort):
    texts = string_list()
    for mod in mi.modules:
      texts.append('from {}.{} import {}'.format(namespace, mi.library, mod))
    if sort:
      texts.sort()
    return texts
  
  @classmethod
  def _expand_one_file(clazz, namespace, filename, sort, dry_run):
    content = file_util.read(filename)
    new_content = clazz.expand_text(namespace, content, sort)
    if new_content == content:
      return
    if dry_run:
      print('DRY_RUN: Would rewrite: {}'.format(filename))
      return
    file_util.save(filename, content = new_content)
    
  _multi_import = namedtuple('_multi_import', 'line, library, modules')
  @classmethod
  def _parse_multi_imports_line(clazz, pattern, line):
    x = re.findall(pattern, line.text)
    if not x:
      return None
    assert len(x) == 1
    assert len(x[0]) == 2
    library = x[0][0]
    modules = [ m.strip() for m in x[0][1].split(',') ]
    return clazz._multi_import(line, library, modules)

  @classmethod
  def _parse_multi_imports(clazz, pattern, lines):
    result = {}
    for line in lines:
      mi = clazz._parse_multi_imports_line(pattern, line)
      if mi and len(mi.modules) > 1:
        result[mi.line.line_number] = mi
    return result
