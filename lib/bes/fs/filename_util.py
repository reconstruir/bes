#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path

from bes.common.check import check

class filename_util(object):
  'Class to deal with file names'

  @classmethod
  def extension(clazz, filename):
    'Return the extension for filename.'
    check.check_string(filename)

    _, ext = path.splitext(filename)
    if ext == '':
      return None
    assert ext[0] == os.extsep
    return ext[1:]
  
  @classmethod
  def has_extension(clazz, filename, extension):
    'Return True if filename has extension.'
    check.check_string(filename)
    check.check_string(extension)
    
    return clazz.extension(filename) == extension
  
  @classmethod
  def has_any_extension(clazz, filename, extensions):
    check.check_string(filename)
    check.check_string_seq(extensions)

    return clazz.extension(filename) in set(extensions)
