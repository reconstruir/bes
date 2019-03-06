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
  def read_to_editor(clazz, filename, throw_error = True):
    if not filename:
      return None
    filename = path.abspath(filename)
    if not path.exists(filename):
      raise IOError('properties file not found: %s' % (filename))
    return properties_editor(filename)
  
  @classmethod
  def read(clazz, filename, throw_error = True):
    editor = clazz.read_to_editor(filename, throw_error = throw_error)
    if not editor:
      return {}
    return editor.properties()

  @classmethod
  def read_to_tuple(clazz, filename, tuple_class, throw_error = True):
    d = clazz.read(filename, throw_error = throw_error)
    values = [ d.get(field, None) for field in tuple_class._fields ]
    return tuple_class(*values)

  @classmethod
  def read_to_tuple_layered(clazz, filenames, tuple_class, throw_error = True):
    d = {}
    for filename in filenames:
      d.update(clazz.read(filename, throw_error = throw_error))
    values = [ d.get(field, None) for field in tuple_class._fields ]
    return tuple_class(*values)
  
