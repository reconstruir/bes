#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import copy

from bes.compat.StringIO import StringIO
from bes.text.text_replace import text_replace

from ..system.check import check
from .object_util import object_util
from .string_util import string_util
from .variable import variable

class dict_util(object):
  'Dict util'

  @staticmethod
  def combine(*dicts):
    result = {}
    for i, n in enumerate(dicts):
      if not isinstance(n, dict):
        raise TypeError('Argument %d is not a dict' % (i + 1))
      result.update(copy.deepcopy(n))
    return result

  @staticmethod
  def update(d, *dicts):
    for i, n in enumerate(dicts):
      if not isinstance(n, dict):
        raise TypeError('Argument %d is not a dict' % (i + 1))
      d.update(copy.deepcopy(n))

  @staticmethod
  def dump(d):
    print(dict_util.dumps(d))

  @staticmethod
  def dumps(d, delimiter = '\n'):
    if not d:
      return ''
    buf = StringIO()
    longest_key = max([ len(key) for key in d.keys() ])
    fmt = '%%%ds: %%s' % (longest_key)
    for k, v in sorted(d.items()):
      buf.write(fmt % (k, v))
      buf.write(delimiter)
    return buf.getvalue()

  @staticmethod
  def filter_with_keys(d, keys):
    'Return a dict with only keys.'
    return { k: v for k,v in d.items() if k in keys }

  @staticmethod
  def filter_without_keys(d, keys):
    'Return a dict with only keys.'
    return { k: v for k,v in d.items() if k not in keys }

  @staticmethod
  def is_homogeneous(d, key_type, value_type):
    'Return True if all items in d are of the given key_type and value_type.'
    for key, value in d.items():
      if not isinstance(key, key_type):
        return False
      if not isinstance(value, value_type):
        return False
    return True

  @staticmethod
  def del_keys(d, *keys):
    'Delete all the given keys from d if present.'
    for key in keys:
      if key in d:
        del d[key]

  @staticmethod
  def unquote_strings(d):
    for k, v in d.items():
      if string_util.is_string(v):
        d[k] = string_util.unquote(v)
        
  @staticmethod
  def quote_strings(d):
    for k, v in d.items():
      if string_util.is_string(v):
        d[k] = string_util.quote(v)

  @staticmethod
  def substitute_variables(d, substitutions, word_boundary = True):
    for key in d.iterkeys():
      current_value = d[key]
      if check.is_string(current_value):
        d[key] = variable.substitute(current_value,
                                     substitutions,
                                     word_boundary = word_boundary)

  @staticmethod
  def replace_values(d, replacements, word_boundary = True):
    for key in d.keys():
      current_value = d[key]
      if check.is_string(current_value):
        d[key] = text_replace.replace(current_value,
                                      replacements,
                                      word_boundary = word_boundary)
      
  @staticmethod
  def del_keys(d, keys):
    keys = object_util.listify(keys)
    for key in keys:
      if key in d:
        del d[key]

  @staticmethod
  def get_recursively(search_dict, field):
    """
    Takes a dict with nested lists and dicts,
    and searches all dicts for a key of the field
    provided.
    """
    fields_found = []

    for key, value in search_dict.items():

        if key == field:
            fields_found.append(value)

        elif isinstance(value, dict):
            results = dict_util.get_recursively(value, field)
            for result in results:
                fields_found.append(result)

        elif isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    more_results = dict_util.get_recursively(item, field)
                    for another_result in more_results:
                        fields_found.append(another_result)

    return fields_found
  
  @staticmethod
  def search(d, key, default=None):
    'https://stackoverflow.com/questions/14962485/finding-a-key-recursively-in-a-dictionary'
    """Return a value corresponding to the specified key in the (possibly
    nested) dictionary d. If there is no item with that key, return
    default.
    """
    stack = [iter(d.items())]
    while stack:
        for k, v in stack[-1]:
            if isinstance(v, dict):
                stack.append(iter(v.items()))
                break
            elif k == key:
                return v
        else:
            stack.pop()
    return default        

  @staticmethod
  def partition_by_function(d, func):
    'Return a dict with only keys.'
    assert callable(func)
    matching = {}
    not_matching = {}
    for key, value in d.items():
      if func(key):
        matching[key] = value
      else:
        not_matching[key] = value
    return matching, not_matching

  @staticmethod
  def hide_passwords(d, password_keys, hide_char = '*'):
    'Return a copy of d with any password kyes hidden.'
    check.check_dict(d, check.STRING_TYPES)
    check.check_string_seq(password_keys)
    check.check_string(hide_char)
    
    result = copy.deepcopy(d)
    for key in password_keys:
      if key in result:
        value = result[key]
        if value != None:
          if not check.is_string(value):
            raise ValueError('value for key "{}" is not a string: "{}"'.format(key, value))
          new_value = hide_char * len(value)
          result[key] = new_value
    return result
    
