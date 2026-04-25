#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

import os.path as path

from bes.common.variable import variable
from bes.system.check import check
from bes.text.text_replace import text_replace

from bes.files.bf_file_ops import bf_file_ops

class file_replace(object):

  ReplaceResult = namedtuple('ReplaceResult', 'included_filenames, excluded_filenames, replaced_filenames')

  @classmethod
  def replace(clazz, filename, replacements, backup = True,
              word_boundary = False, word_boundary_chars = None):
    check.check_string(filename)
    check.check_dict(replacements, check.STRING_TYPES, check.STRING_TYPES)
    check.check_bool(backup)
    check.check_bool(word_boundary)
    check.check_set(word_boundary_chars, allow_none = True)
    
    content = bf_file_ops.read(filename, codec = 'utf-8')
    new_content = text_replace.replace(content, replacements,
                                       word_boundary = word_boundary,
                                       word_boundary_chars = word_boundary_chars)
    if content == new_content:
      return False
    if backup:
      bf_file_ops.backup(filename)
    bf_file_ops.save(filename, content = new_content.encode('utf-8'), mode = bf_file_ops.mode(filename))
    return True

  @classmethod
  def replace_many(clazz, filenames, replacements, backup = True, test_func = None):
    included_filenames = []
    excluded_filenames = []
    replaced_filenames = []
    for filename in filenames:
      include = True
      if test_func:
        include = test_func(filename)
      if include:
        included_filenames.append(filename)
        if clazz.replace(filename, replacements, backup = backup):
          replaced_filenames.append(filename)
      else:
        excluded_filenames.append(filename)
    return clazz.ReplaceResult(included_filenames, excluded_filenames, replaced_filenames)

  @classmethod
  def copy_with_substitute(clazz, src, dst, replacements, backup = True):
    assert isinstance(replacements, dict)
    content = bf_file_ops.read(src, 'utf-8')
    new_content = variable.substitute(content, replacements)
    old_content = None
    if path.exists(dst):
      old_content = bf_file_ops.read(dst, 'utf-8')
      if old_content == new_content:
        return False
    if backup:
      bf_file_ops.backup(dst)
    bf_file_ops.save(dst, content = new_content, mode = bf_file_ops.mode(src))
    return True
