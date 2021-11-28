#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.common.check import check

class file_check(object):

  @classmethod
  def check_file(clazz, filename, exception_class = None, allow_none = False):
    check.check_string(filename, allow_none = allow_none)
    check.check_class(exception_class, allow_none = True)

    exception_class = exception_class or IOError

    if allow_none and filename == None:
      return None
    if not path.exists(filename):
      raise exception_class('File not found: %s' % (filename))
    if not path.isfile(filename) or path.islink(filename):
      raise exception_class('Not a file: %s' % (filename))
    return path.abspath(filename)

  @classmethod
  def check_dir(clazz, dirname, exception_class = None, allow_none = False):
    check.check_string(dirname, allow_none = allow_none)
    check.check_class(exception_class, allow_none = True)

    exception_class = exception_class or IOError

    if allow_none and dirname == None:
      return None
    if not path.exists(dirname):
      raise exception_class('Directory not found: %s' % (dirname))
    if not path.isdir(dirname):
      raise exception_class('Not a directory: %s' % (dirname))
    return path.abspath(dirname)

  @classmethod
  def check_dir_seq(clazz, dirs, exception_class = None):
    check.check_string_seq(dirs)
    check.check_class(exception_class, allow_none = True)

    result = []
    for d in dirs:
      result.append(clazz.check_dir(d, exception_class = exception_class))
    return result
