#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os.path as path
from bes.common import check

class file_check(object):

  @classmethod
  def check_file(clazz, filename):
    check.check_string(filename)
    if not path.exists(filename):
      raise IOError('File not found: %s' % (filename))
    if path.isfile(filename):
      return
    if path.islink(filename):
      return
      raise IOError('Not a file: %s' % (filename))

  @classmethod
  def check_dir(clazz, dirname):
    check.check_string(dirname)
    if not path.exists(dirname):
      raise IOError('File not found: %s' % (dirname))
    if not path.isdir(dirname):
      raise IOError('Not a directory: %s' % (dirname))
