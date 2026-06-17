#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import string
from collections import namedtuple

from ..system.check import check

from .simple_config_error import simple_config_error

class simple_config_options(object):

  KEY_CHECK_ATTRIB = 'attrib'
  KEY_CHECK_ANY = 'any'
  KEY_CHECK_FNMATCH = 'fnmatch'

  VALID_KEY_CHECKS = ( KEY_CHECK_ATTRIB, KEY_CHECK_ANY, KEY_CHECK_FNMATCH )

  def __init__(self, *args, **kargs):
    self.log_tag = 'simple_config'
    self.key_check_type = self.KEY_CHECK_ATTRIB
    for key, value in kargs.items():
      setattr(self, key, value)
    check.check_string(self.log_tag)
    check.check_string(self.key_check_type)
    if self.key_check_type not in self.VALID_KEY_CHECKS:
      raise simple_config_error('Invalid key check type: "{}".  Should be one of: {}'.format(self.key_check_type,
                                                                                             ' '.join(self.VALID_KEY_CHECKS)))

  def validate_key(self, key, origin):
    check.check_string(key)
    check.check_simple_config_origin(origin)

    if len(key) < 1:
      raise simple_config_error('Invalid key: "{}"'.format(key))
    first_chars, next_chars = self._VALID_KEY_CHARS[self.key_check_type]
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

  _valid_key_chars = namedtuple('_valid_key_chars', 'first_chars, next_chars')
  _VALID_KEY_CHARS = {
    KEY_CHECK_ATTRIB: _valid_key_chars(_ENTRY_KEY_VALID_FIRST_CHAR,
                                       _ENTRY_KEY_VALID_NEXT_CHARS),
    KEY_CHECK_FNMATCH: _valid_key_chars(_ENTRY_KEY_VALID_CHARS_FNMATCH,
                                        _ENTRY_KEY_VALID_CHARS_FNMATCH),
    KEY_CHECK_ANY: _valid_key_chars(None, None),
  }

check.register_class(simple_config_options)
