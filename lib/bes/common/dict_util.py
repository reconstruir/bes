#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import copy
from bes.compat import StringIO
from .string_util import string_util
from .variable import variable
from .object_util import object_util

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
      d[key] = variable.substitute(d[key], substitutions, word_boundary = word_boundary)

  @staticmethod
  def replace_values(d, replacements, word_boundary = True):
    for key in d.keys():
      d[key] = string_util.replace(d[key], replacements)
      
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

    for key, value in search_dict.iteritems():

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
