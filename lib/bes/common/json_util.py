#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import json
import os
import shutil

from .object_util import object_util

from bes.system.check import check

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
  def to_json(clazz, o, indent = None, sort_keys = False, ensure_last_line_sep = False, use_default = True):
    check.check_int(indent, allow_none = True)
    check.check_bool(sort_keys)
    check.check_bool(ensure_last_line_sep)

    indent = 2 if indent == None else indent
    
    '''
    Like json.dumps plus the following:
     - same white space results on both python 2 and 3
     - __dict__ is used when object is not json encodable
    '''
    def _default(o):
      try:
        return o.__dict__
      except Exception as ex:
        print(f'json encoding failed on {o.__class__} {o}', flush = True)
        raise
    default = _default if use_default else None
    js = json.dumps(o, indent = indent, default = default, sort_keys = sort_keys, separators = (', ', ': '))
    if not ensure_last_line_sep:
      return js
    return js + os.linesep

  @classmethod
  def normalize(clazz, o):
    return json.loads(json_util.to_json(o, indent = 2))

  @classmethod
  def normalize_text(clazz, text, sort_keys = False):
    check.check_string(text)
    
    o = json.loads(text)
    return json_util.to_json(o, indent = 2, sort_keys = sort_keys)

  @classmethod
  def read_file(clazz, filename, codec = None):
    check.check_string(filename)
    check.check_string(codec, allow_none = True)
    
    codec = codec or 'utf-8'
    with open(filename, 'r', encoding = codec) as f:
      content = f.read()
      return json.loads(content)
    return None
    
  @classmethod
  def save_file(clazz, filename, o, indent = None, sort_keys = False, codec = None, ensure_last_line_sep = False):
    check.check_string(filename)
    check.check_int(indent, allow_none = True)
    check.check_bool(sort_keys)
    check.check_string(codec, allow_none = True)
    check.check_bool(ensure_last_line_sep)

    content = clazz.to_json(o,
                            indent = indent,
                            sort_keys = sort_keys,
                            ensure_last_line_sep = ensure_last_line_sep)
    codec = codec or 'utf-8'
    with open(filename, 'w', encoding = codec) as f:
      f.write(content)

  @classmethod
  def normalize_file(clazz, filename, codec = None, backup = False):
    check.check_string(filename)
#    check.check_int(indent, allow_none = True)
#    check.check_bool(sort_keys)
    check.check_string(codec, allow_none = True)

    o = clazz.read_file(filename, codec = codec)
    if backup:
      shutil.copy(filename, f'{filename.bak}')
    clazz.save_file(filename, o, indent = 2, sort_keys = True, codec = codec)
