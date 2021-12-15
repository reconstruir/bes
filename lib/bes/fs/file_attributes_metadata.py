#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system.check import check

from .file_attributes import file_attributes
from .file_mime import file_mime
from .file_util import file_util

class file_attributes_metadata(object):

  _KEY_BES_MIME_TYPE = 'bes_mime_time'
  
  @classmethod
  def get_bytes(clazz, filename, key, value_maker):
    check.check_string(filename)
    check.check_string(key)
    check.check_function(value_maker)

    mtime_key = clazz._make_mtime_key(key)
    attr_mtime = file_attributes.get_date(filename, mtime_key)
    file_mtime = file_util.get_modification_date(filename)

    if attr_mtime == None:
      value = value_maker()
      file_attributes.set_bytes(filename, key, value)
      file_attributes.set_date(filename, mtime_key, file_mtime)
      return value

    if attr_mtime == file_mtime:
      if file_attributes.has_key(filename, key):
        return file_attributes.get_bytes(filename, key)

    value = value_maker()
    file_attributes.set_bytes(filename, key, value)
    file_attributes.set_date(filename, mtime_key, file_mtime)
    return value

  @classmethod
  def get_mime_type(clazz, filename):
    def _value_maker():
      return file_mime.mime_type(filename).encode('utf-8')
    return clazz.get_bytes(filename, clazz._KEY_BES_MIME_TYPE, _value_maker).decode('utf-8')
    
  @classmethod
  def _make_mtime_key(clazz, key):
    return '__bes_mtime_{}__'.format(key)
