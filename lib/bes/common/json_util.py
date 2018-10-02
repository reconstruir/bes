#!/usr/bin/env python
#-*- coding:utf-8 -*-

import json
from .object_util import object_util

class json_util(object):
  'Json util'

  @classmethod
  def can_encode(clazz, o):
    'Return true if the given object can be encoded as json.'
    try:
      clazz.to_json(o)
      return True
    except Exception as ex:
      return False

  @classmethod
  def to_json(clazz, o, indent = None, sort_keys = False):
    '''
    Like json.dumps plus the following:
     - same white space results on both python 2 and 3
     - __dict__ is used when object is not json encodable
    '''
    def default(o): return o.__dict__
    return json.dumps(o, indent = indent, default = default, sort_keys = sort_keys, separators = (', ', ': '))

  @classmethod
  def normalize(clazz, o):
    return json.loads(json_util.to_json(o, indent = 2))

  @classmethod
  def read_file(clazz, filename):
    with open(filename, 'r') as f:
      return json.loads(f.read())
    return None
    
  @classmethod
  def save_file(clazz, filename, o, indent = None, sort_keys = False):
    content = clazz.to_json(o, indent = indent, sort_keys = sort_keys)
    with open(filename, 'w') as f:
      f.write(content)

