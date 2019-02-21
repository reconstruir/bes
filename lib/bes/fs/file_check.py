#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.common import check

class file_check(object):

  @classmethod
  def check_file(clazz, filename):
    check.check_string(filename)
    if not path.exists(filename):
      raise IOError('File not found: %s' % (filename))
    if not path.isfile(filename) or path.islink(filename):
      raise IOError('Not a file: %s' % (filename))
    return filename

  @classmethod
  def check_dir(clazz, dirname):
    check.check_string(dirname)
    if not path.exists(dirname):
      raise IOError('Directory not found: %s' % (dirname))
    if not path.isdir(dirname):
      raise IOError('Not a directory: %s' % (dirname))
    return dirname
