#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.common.check import check

class file_check(object):

  @classmethod
  def check_file(clazz, filename, exception_class = None):
    check.check_string(filename)
    check.check_class(exception_class, allow_none = True)

    exception_class = exception_class or IOError
    if not path.exists(filename):
      raise exception_class('File not found: %s' % (filename))
    if not path.isfile(filename) or path.islink(filename):
      raise exception_class('Not a file: %s' % (filename))
    return filename

  @classmethod
  def check_dir(clazz, dirname, exception_class = None):
    check.check_string(dirname)
    check.check_class(exception_class, allow_none = True)

    exception_class = exception_class or IOError
    if not path.exists(dirname):
      raise exception_class('Directory not found: %s' % (dirname))
    if not path.isdir(dirname):
      raise exception_class('Not a directory: %s' % (dirname))
    return dirname
