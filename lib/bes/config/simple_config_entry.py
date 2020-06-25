#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common.check import check
from bes.compat.StringIO import StringIO
from bes.key_value.key_value import key_value
from bes.key_value.key_value_list import key_value_list

from collections import namedtuple

class simple_config_entry(namedtuple('simple_config_entry', 'value, origin, annotations, hints')):

  def __new__(clazz, value, origin = None, annotations = None, hints = None):
    check.check_key_value(value)
    check.check_simple_config_origin(origin, allow_none = True)
    check.check_key_value_list(annotations, allow_none = True)
    check.check_dict(hints, allow_none = True)
    
    return clazz.__bases__[0].__new__(clazz, value, origin, annotations, hints)
    
  def __str__(self):
    buf = StringIO()
    buf.write(self.value.key)
    if self.annotations:
      buf.write('[')
      for i, annotation in enumerate(self.annotations):
        if i != 0:
          buf.write(',')
        buf.write(annotation.key)
        if annotation.value:
          buf.write('=')
          buf.write(annotation.value)
      buf.write(']')
    buf.write(': ')
    buf.write(self.value.value)
    return buf.getvalue()

  def has_annotation(self, annotation_key):
    check.check_string(annotation_key)
    return self.find_annotation(annotation_key) is not None

  def find_annotation(self, annotation_key):
    check.check_string(annotation_key)
    if not self.annotations:
      return None
    return self.annotations.find_by_key(annotation_key)
  
check.register_class(simple_config_entry)
