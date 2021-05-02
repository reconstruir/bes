#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common.check import check
from bes.common.dict_util import dict_util
from bes.script.blurber import blurber

class python_installer_options(object):
  
  def __init__(self, *args, **kargs):
    self.verbose = False
    self.blurber = blurber()
    self.installer_name = None
    self.system = None
    self.dry_run = False
    for key, value in kargs.items():
      setattr(self, key, value)
    check.check_bool(self.verbose)
    check.check_blurber(self.blurber)
    check.check_string(self.installer_name, allow_none = True)
    check.check_string(self.system, allow_none = True)
    check.check_bool(self.dry_run)

check.register_class(python_installer_options)
