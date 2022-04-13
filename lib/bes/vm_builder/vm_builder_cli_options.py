#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from ..system.check import check
from bes.common.dict_util import dict_util

class vm_builder_cli_options(object):

  def __init__(self, *args, **kargs):
    self.dont_include_ip_address = False
    self.dont_include_comment = False
    for key, value in kargs.items():
      setattr(self, key, value)
    check.check_bool(self.dont_include_ip_address)
    check.check_bool(self.dont_include_comment)

check.register_class(vm_builder_cli_options)
