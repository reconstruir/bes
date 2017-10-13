#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os.path as path
from bes.common import string_util, variable
from .file_util import file_util
from collections import namedtuple

class file_replace(object):

  ReplaceResult = namedtuple('ReplaceResult', 'included_filenames,excluded_filenames,replaced_filenames')

  @classmethod
  def replace(clazz, filename, replacements, backup = True, word_boundary = False):
    assert isinstance(replacements, dict)
    content = file_util.read(filename, codec = 'utf-8')
    new_content = string_util.replace(content, replacements, word_boundary = word_boundary)
    if content == new_content:
      return False
    if backup:
      file_util.backup(filename)
    file_util.save(filename, content = new_content.encode('utf-8'), mode = file_util.mode(filename))
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
    content = file_util.read(src, 'utf-8')
    new_content = variable.substitute(content, replacements)
    old_content = None
    if path.exists(dst):
      old_content = file_util.read(dst, 'utf-8')
      if old_content == new_content:
        return False
    if backup:
      file_util.backup(dst)
    file_util.save(dst, content = new_content, mode = file_util.mode(src))
    return True
