#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple
import os, os.path as path, re

from bes.fs import file_util
from bes.text.string_list import string_list
from bes.text.text_line_parser import text_line_parser

from .files import files

class import_expand(object):

  @classmethod
  def expand(clazz, namespace, files, sort, dry_run, verbose):
    for filename in files:
      clazz._expand_one_file(namespace, filename, sort, dry_run, verbose)

  @classmethod
  def expand_text(clazz, namespace, text, sort):
    pattern = r'^(\s*)from\s+{}\.(.+)\s+import\s+(.+)\s*$'.format(namespace)
    lines = text_line_parser(text)
    mi_imports = clazz._parse_multi_imports(pattern, lines)
    if not mi_imports:
      return text
    line_numbers = sorted(mi_imports.keys())
    offset = 0
    for original_line_number in line_numbers:
      line_number = original_line_number + offset
      mi = mi_imports[original_line_number]
      texts = clazz._make_texts(namespace, mi, sort)
      #clazz._dump_lines(lines, 'RUN{} BEFORE '.format(original_line_number))
      lines.replace_line_with_lines(line_number, texts, renumber = True)
      #clazz._dump_lines(lines, 'RUN{}  AFTER '.format(original_line_number))
      offset += (len(texts) - 1)
    return str(lines).rstrip() + '\n'

  @classmethod
  def _dump_lines(clazz, lines, blurb):
    x = text_line_parser(lines)
    x.prepend(blurb)
    x.add_line_numbers()
    print(str(x))
  
  @classmethod
  def _make_texts(clazz, namespace, mi, sort):
    texts = string_list()
    for mod in mi.modules:
      texts.append('{}from {}.{} import {}'.format(mi.indent, namespace, mi.library, mod))
    if sort:
      texts.sort()
    return texts
  
  @classmethod
  def _expand_one_file(clazz, namespace, filename, sort, dry_run, verbose):
    content = file_util.read(filename)
    new_content = clazz.expand_text(namespace, content, sort)
    if new_content == content:
      return
    if dry_run:
      print('DRY_RUN: Would rewrite: {}'.format(filename))
      return
    file_util.save(filename, content = new_content)
    if verbose:
      print('Updated: {}'.format(filename))
    
  _multi_import = namedtuple('_multi_import', 'line, indent, library, modules')
  @classmethod
  def _parse_multi_imports_line(clazz, pattern, line):
    x = re.findall(pattern, line.text)
    if not x:
      return None
    assert len(x) == 1
    assert len(x[0]) == 3
    indent = x[0][0]
    library = x[0][1]
    modules = [ m.strip() for m in x[0][2].split(',') ]
    return clazz._multi_import(line, indent, library, modules)

  @classmethod
  def _parse_multi_imports(clazz, pattern, lines):
    result = {}
    for line in lines:
      mi = clazz._parse_multi_imports_line(pattern, line)
      if mi and len(mi.modules) > 1:
        result[mi.line.line_number] = mi
    return result
