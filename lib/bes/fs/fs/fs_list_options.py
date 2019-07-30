#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common.check import check

class fs_list_options(object):
  def __init__(self, *args, **kargs):
    self.recursive = False
    for key, value in kargs.items():
      setattr(self, key, value)
    check.check_bool(self.recursive)
check.register_class(fs_list_options)
