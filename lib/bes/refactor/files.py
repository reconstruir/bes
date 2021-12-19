#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple
import os, os.path as path, re, sys

from bes.common.algorithm import algorithm
from bes.common.string_util import string_util
from bes.fs.file_check import file_check
from bes.fs.file_find import file_find
from bes.fs.file_match import file_match
from bes.fs.file_mime import file_mime
from bes.fs.file_path import file_path
from bes.fs.file_path import file_path
from bes.fs.file_replace import file_replace
from bes.fs.file_search import file_search
from bes.fs.file_util import file_util
from bes.git.git import git
from bes.text.string_list import string_list
from bes.text.text_line_parser import text_line_parser

class files(object):

  @classmethod
  def resolve_files(clazz, *files_or_dirs):
    'Resolve a mixed list of files and directories into a sorted list of files.'
    result = []
    for filename in files_or_dirs:
      result += clazz._resolve_one(filename)
    return sorted(algorithm.unique(result))

  @classmethod
  def filter_files(filenames, include_patterns, exclude_patterns):
    'Resolve a mixed list of files and directories into a sorted list of files.'
    result = file_match.fnmatch(filenames, exclude_patterns, file_match.NONE)
    return file_match.fnmatch(result, include_patterns, file_match.ANY)

  @classmethod
  def _resolve_one(clazz, filename):
    'Resolve a mixed list of files and directories into a sorted list of files.'
    if not string_util.is_string(filename):
      raise RuntimeError('Not a string: %s' % (filename))
    if not path.exists(filename):
      raise RuntimeError('Not found: %s' % (filename))
    if path.isfile(filename):
      return [ clazz._resolve_one_file(filename) ]
    elif path.isdir(filename):
      return file_find.find(filename, relative = False)
    else:
      raise RuntimeError('Not a file or directory: %s' % (filename))
    
  @classmethod
  def _resolve_one_file(clazz, filename):
    return path.abspath(path.normpath(filename))

  @classmethod
  def find_text_files(clazz, d):
    'Find text files recurisively in directory d.'
    return file_find.find_function(d, file_mime.is_text, relative = False, match_basename = False)

  @classmethod
  def find_python_files(clazz, d):
    'Find python files recurisively in directory d.'
    return [ f for f in clazz.find_text_files(d) if f.lower().endswith('.py') ]

  @classmethod
  def text_files(clazz, filenames):
    'Return only the text files in filesnames.'
    return file_match.match_function(filenames, file_mime.is_text)

  @classmethod
  def search_files(clazz, filenames, text, word_boundary = False, ignore_case = False):
    'Return only the text files in filesnames.'
    result = []
    for filename in filenames:
      result += file_search.search_file(filename, text, word_boundary = word_boundary, ignore_case = ignore_case)
    return result

  @classmethod
  def match_files(clazz, filenames, text, word_boundary = False, ignore_case = False):
    search_rv = clazz.search_files(filenames, text, word_boundary = word_boundary)
    return algorithm.unique([ s.filename for s in search_rv ])

  @classmethod
  def rename_subdirs(clazz, where, src, dst):
    assert path.isdir(where)
    dirs = file_find.find(where, file_type = file_find.DIR)
    dirs = file_match.match_function(dirs, lambda f: src in f)
    while dirs:
      dir_depths = [ file_path.depth(d) for d in dirs ]
      dir_and_depths = sorted(zip(dir_depths, dirs), reverse = True)
      new_dirs = []
      for _, dirname in dir_and_depths:
        new_dirname = file_path.replace(dirname, src, dst, count = 1, backwards = True)
        assert new_dirname != dirname
        abs_dirname = path.join(where, dirname)
        abs_new_dirname = path.join(where, new_dirname)
        clazz._rename(abs_dirname, abs_new_dirname)
        new_dirs.append(new_dirname)
      dirs = file_match.match_function(new_dirs, lambda f: src in f)

  @classmethod
  def rename_files(clazz, where, src, dst):
    assert path.isdir(where)
    filenames = file_find.find(where, file_type = file_find.FILE)
    matching = file_match.match_function(filenames, lambda f: src in f)
    for filename in matching:
      new_filename = filename.replace(src, dst)
      abs_new_filename = path.join(where, new_filename)
      abs_filename = path.join(where, filename)
      clazz._rename(abs_filename, abs_new_filename)
      
  @classmethod
  def _rename(clazz, old, new):
    try:
      git.move(os.getcwd(), old, new)
    except Exception as ex:
      file_util.rename(old, new)

  @classmethod
  def _refactor_one_dir(clazz, src, dst, where, word_boundary = False):
    where = path.normpath(where)
    if '..' in where:
      raise RuntimeError('Invalid path - dont use \"..\" : %s' % (where))
    abs_where = path.abspath(where)
    text_files = clazz.find_text_files(abs_where)
    matching_files = clazz.match_files(text_files, src, word_boundary = word_boundary)
    replacements = { src: dst }
    for filename in matching_files:
      file_replace.replace(filename, replacements, backup = False, word_boundary = word_boundary)
    clazz.rename_subdirs(abs_where, src, dst)
    clazz.rename_files(abs_where, src, dst)
    abs_new_where = file_path.replace(abs_where, src, dst, count = 1, backwards = True)
    if abs_new_where != abs_where:
      file_util.rename(abs_where, abs_new_where)

  @classmethod
  def refactor(clazz, src, dst, dirs, word_boundary = False):
    assert isinstance(dirs, list)
    if src == dst:
      raise RuntimeError('src and dst are the same: %s' % (src))
    for d in dirs:
      clazz._refactor_one_dir(src, dst, d, word_boundary = word_boundary)

  @classmethod
  def rename_dirs(clazz, src_pattern, dst_pattern, root_dir, word_boundary = False):
    assert src_pattern
    assert dst_pattern
    assert not src_pattern in dst_pattern
    assert not dst_pattern in src_pattern
    
    root_dir = path.abspath(root_dir)
    file_check.check_dir(root_dir)
    while True:
      dirs = file_find.find(root_dir, relative = True, file_type = file_find.DIR)
      dirs = [ d for d in dirs if src_pattern in d ]
      dirs = clazz._minimum_paths(dirs, src_pattern)
      if not dirs:
        return
      src_dir = dirs[0]
      dst_dir = src_dir.replace(src_pattern, dst_pattern)
      file_util.rename(src_dir, dst_dir)

  @classmethod
  def _minimum_path(clazz, p, src_pattern):
    v = file_path.split(p)
    result = []
    for x in v:
      result.append(x)
      if src_pattern in x:
        break
    return file_path.join(result)

  @classmethod
  def _minimum_paths(clazz, paths, src_pattern):
    return algorithm.unique([ clazz._minimum_path(p, src_pattern) for p in paths ])
