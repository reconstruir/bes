#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

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
    
check.register_class(simple_config_options)
