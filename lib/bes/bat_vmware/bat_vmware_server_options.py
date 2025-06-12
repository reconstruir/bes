#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from ..system.check import check
from bes.common.dict_util import dict_util
from bes.script.blurber import blurber

class bat_vmware_server_options(object):
  
  def __init__(self, *args, **kargs):
    self.verbose = False
    self.port = None
    self.hostname = None
    self.blurber = blurber()
    for key, value in kargs.items():
      setattr(self, key, value)
    check.check_bool(self.verbose)
    check.check_blurber(self.blurber)
    check.check_int(self.port, allow_none = True)
    check.check_string(self.hostname, allow_none = True)

check.register_class(bat_vmware_server_options)
