#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple
import os, os.path as path, re

from bes.common import string_util
from bes.fs import file_util
from bes.text.string_list import string_list
from bes.text.text_line_parser import text_line_parser

from .files import files

class import_expand(object):

  _PATTERN = r'^(\s*)from\s+([a-zA-Z_\.][a-zA-Z0-9_\.]+)\s+import\s+(.+)\s*$'
  
  @classmethod
  def expand(clazz, namespace, files, include_module, sort, dry_run, verbose):
    for filename in files:
      clazz._expand_one_file(namespace, filename, include_module, sort, dry_run, verbose)

  @classmethod
  def expand_text(clazz, namespace, text, sort, include_module):
    lines = text_line_parser(text)
    mi_imports = clazz._parse_multi_imports(clazz._PATTERN, namespace, lines)
    if not mi_imports:
      return text
    line_numbers = sorted(mi_imports.keys())
    offset = 0
    for original_line_number in line_numbers:
      line_number = original_line_number + offset
      mi = mi_imports[original_line_number]
      texts = clazz._make_texts(namespace, mi, sort, include_module)
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
  def _make_texts(clazz, namespace, mi, sort, include_module):
    texts = string_list()
    for mod in mi.modules:
      texts.append(clazz._make_new_import_line(mi.indent, namespace, mi.library, mod, include_module))
    if sort:
      texts.sort()
    return texts
  
  @classmethod
  def _make_new_import_line(clazz, indent, namespace, library, mod, include_module):
    if mod.alias:
      alias_part = ' as {}'.format(mod.alias)
    else:
      alias_part = ''
    if include_module:
      import_library = '{}.{}.{}'.format(namespace, library, mod.name)
    else:
      import_library = '{}.{}'.format(namespace, library)
    import_library = string_util.remove_tail(import_library, '.')
    import_library = import_library.replace('..', '.')
    result = '{}from {} import {}{}'.format(indent, import_library, mod.name, alias_part)
    return result
  
  @classmethod
  def _expand_one_file(clazz, namespace, filename, include_module, sort, dry_run, verbose):
    content = file_util.read(filename)
#    if verbose:
#      print('Trying: {}'.format(filename))
    new_content = clazz.expand_text(namespace, content, sort, include_module)
    if new_content == content:
      return
    if dry_run:
      print('DRY_RUN: Would rewrite: {}'.format(filename))
      return
    file_util.save(filename, content = new_content)
    if verbose:
      print('Updated: {}'.format(filename))
    
  _multi_import = namedtuple('_multi_import', 'line, indent, library, modules')
  _module = namedtuple('_module', 'name, alias')
  @classmethod
  def _parse_multi_imports_line(clazz, pattern, namespace, line):
    x = re.findall(pattern, line.text)
    if not x:
      return None
    if len(x[0]) != 3:
      return None
    indent = x[0][0]
    library_head = x[0][1]
    if not library_head.startswith(namespace):
      return None
    library = string_util.remove_head(library_head, namespace)
    library = string_util.remove_head(library, '.')
    modules = clazz._parse_modules(x[0][2])
    return clazz._multi_import(line, indent, library, modules)

  @classmethod
  def _parse_modules(clazz, modules):
    return [ clazz._parse_module(m) for m in modules.split(',') ]
  
  @classmethod
  def _parse_module(clazz, m):
    name, delimiter, alias = m.partition(' as ')
    name = name.strip()
    alias = alias.strip() or None
    return clazz._module(name, alias)
  
  @classmethod
  def _parse_multi_imports(clazz, pattern, namespace, lines):
    result = {}
    for line in lines:
      mi = clazz._parse_multi_imports_line(pattern, namespace, line)
      if mi and len(mi.modules) > 1:
        result[mi.line.line_number] = mi
    return result
