#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common.check import check

class vfs_list_options(object):

  def __init__(self, *args, **kargs):
    self.flat_paths = False
    self.human_friendly = False
    self.one_line = False
    self.recursive = False
    self.show_attributes = False
    self.show_checksums = False
    self.show_details = False
    for key, value in kargs.items():
      setattr(self, key, value)
    check.check_bool(self.flat_paths)
    check.check_bool(self.human_friendly)
    check.check_bool(self.one_line)
    check.check_bool(self.recursive)
    check.check_bool(self.show_attributes)
    check.check_bool(self.show_checksums)
    check.check_bool(self.show_details)
    
  def __str__(self):
    return str(self.__dict__)
    
check.register_class(vfs_list_options)
