#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple
from os import path
from bes.common import check

from .properties_editor import properties_editor

class properties_file(object):
  '''
  A class to read properties files.
  '''

  @classmethod
  def read(clazz, filename, throw_error = True):
    if not filename:
      return {}
    filename = path.abspath(filename)
    if not path.exists(filename):
      raise IOError('properties file not found: %s' % (filename))
    editor = properties_editor(filename)
    return editor.properties()
