#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common.check import check

class fs_list_options(object):
  def __init__(self, *args, **kargs):
    self.recursive = False
    self.show_details = False
    self.one_line = False
    for key, value in kargs.items():
      setattr(self, key, value)
    check.check_bool(self.recursive)
    check.check_bool(self.show_details)
    check.check_bool(self.one_line)
check.register_class(fs_list_options)
