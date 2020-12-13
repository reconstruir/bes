#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import tempfile

from bes.common.check import check
from bes.common.dict_util import dict_util
from bes.script.blurber import blurber

class package_manager_options(object):
  
  def __init__(self, *args, **kargs):
    self.verbose = False
    self.password = None
    self.blurber = blurber()
    self.working_dir = tempfile.gettempdir()
    self.prompt = 'sudo password: '
    self.force_auth = False
    self.error_message = None
    self.allow_root_dir_removal = False
    for key, value in kargs.items():
      setattr(self, key, value)
    check.check_bool(self.verbose)
    check.check_string(self.password, allow_none = True)
    check.check_blurber(self.blurber)
    check.check_string(self.working_dir, allow_none = True)
    check.check_string(self.prompt, allow_none = True)
    check.check_bool(self.force_auth)
    check.check_string(self.error_message, allow_none = True)
    check.check_bool(self.allow_root_dir_removal)

  def __str__(self):
    return str(dict_util.hide_passwords(self.__dict__, [ 'password' ]))

check.register_class(package_manager_options)
