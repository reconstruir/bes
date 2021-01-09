#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common.check import check
from bes.script.blurber import blurber

class vmware_options(object):
  
  def __init__(self, *args, **kargs):
    self.verbose = False
    for key, value in kargs.items():
      setattr(self, key, value)
    check.check_bool(self.verbose)

check.register_class(vmware_options)
