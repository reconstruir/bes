#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path
import os
from bes.common import check
from bes.system import execute

from ._file_attributes_base import _file_attributes_base

class _file_attributes_linux(_file_attributes_base):

  @classmethod
  #@abstractmethod
  def get(clazz, filename, key):
    'Return the attribute value with key for filename.'
    check.check_string(filename)
    check.check_string(key)
    rv = clazz._call_attr('-q', '-g', key, filename)
    if rv.exit_code == 0:
      return rv.stdout.strip()
    else:
      if path.exists(filename) and os.access(filename, os.R_OK):
        return None
      else:
        raise RuntimeError('error getting \"%s\" for %s' % (key, filename))

  @classmethod
  #@abstractmethod
  def set(clazz, filename, key, value):
    'Set the value of attribute with key to value for filename.'
    check.check_string(filename)
    check.check_string(key)
    check.check_string(value)
    if ' ' in key:
      raise ValueError('space not supported in key: \"%s\"' % (key))
    rv = clazz._call_attr('-q', '-s', key, '-V', value, filename)
    if rv.exit_code != 0:
      raise RuntimeError('error setting attribute \"%s\" for %s: %s' % (key, filename, rv.stdout.strip()))
  
  @classmethod
  #@abstractmethod
  def remove(clazz, filename, key):
    'Remove the attirbute with key from filename.'
    check.check_string(filename)
    check.check_string(key)
    clazz._call_attr('-r', key, filename)
  
  @classmethod
  #@abstractmethod
  def keys(clazz, filename):
    'Return all the keys set for filename.'
    rv = clazz._call_attr('-q', '-l', filename)
    if rv.exit_code != 0:
      raise RuntimeError('error getting keys for %s: %s' % (filename, rv.stdout.strip()))
    text = rv.stdout.strip()
    keys = [ line for line in text.split('\n') if line.strip() ]
    return sorted(keys)

  @classmethod
  #@abstractmethod
  def clear(clazz, filename):
    'Create all attributes.'
    check.check_string(filename)
    for key in clazz.keys(filename):
      clazz.remove(filename, key)
      
  @classmethod
  def _call_attr(clazz, *args):
    'Call attr with args.'
    cmd = [ 'attr' ] + list(args or [])
    return execute.execute(cmd, shell = False, raise_error = False)
