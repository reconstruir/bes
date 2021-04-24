#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import string

from collections import namedtuple

from bes.common.check import check

from .simple_config_error import simple_config_error

class simple_config_keys(object):

  KEY_CHECK_ATTRIB = 'attrib'
  KEY_CHECK_ANY = 'any'
  KEY_CHECK_FNMATCH = 'fnmatch'

  KEY_CHECK_TYPES = ( KEY_CHECK_ATTRIB, KEY_CHECK_ANY, KEY_CHECK_FNMATCH )

  @classmethod
  def check_key_check(clazz, key_check_type):
    check.check_string(key_check_type)

    if key_check_type not in clazz.KEY_CHECK_TYPES:
      raise simple_config_error('Invalid key check type: "{}".  Should be one of: {}'.format(key_check_type,
                                                                                            ' '.join(clazz.KEY_CHECK_TYPES)))
    return key_check_type

  @classmethod
  def validate_key(clazz, key_check_type, key, origin):
    clazz.check_key_check(key_check_type)
    check.check_string(key)
    check.check_simple_config_origin(origin)

    if len(key) < 1:
      raise simple_config_error('Invalid key: "{}"'.format(key))
    
    first_chars, next_chars = clazz._VALID_KEY_CHARS[key_check_type]
    if first_chars:
      if not key[0] in first_chars:
        raise simple_config_error('invalid config key first char: "{}"'.format(key), origin)

    if next_chars:
      if len(key) > 1:
        for i, c in enumerate(key[1:]):
          if not c in next_chars:
            raise simple_config_error('invalid config key char {}: "{}"'.format(i + 2, key))
    
  _ENTRY_KEY_VALID_FIRST_CHAR = string.ascii_letters + '_'
  _ENTRY_KEY_VALID_NEXT_CHARS = _ENTRY_KEY_VALID_FIRST_CHAR + string.digits
  _ENTRY_KEY_VALID_CHARS_FNMATCH = _ENTRY_KEY_VALID_NEXT_CHARS + '*' + '+' + '?' + '[' + ']' + '.'

  valid_key_chars = namedtuple('valid_key_chars', 'first_chars, next_chars')
  _VALID_KEY_CHARS = {
    KEY_CHECK_ATTRIB: valid_key_chars(_ENTRY_KEY_VALID_FIRST_CHAR,
                                      _ENTRY_KEY_VALID_NEXT_CHARS),
    KEY_CHECK_FNMATCH: valid_key_chars(_ENTRY_KEY_VALID_CHARS_FNMATCH,
                                       _ENTRY_KEY_VALID_CHARS_FNMATCH),
    KEY_CHECK_ANY: valid_key_chars(None, None),
  }    
  
