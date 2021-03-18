#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common.check import check
from bes.script.blurber import blurber
from bes.property.cached_property import cached_property

class pip_installer_options(object):
  
  def __init__(self, *args, **kargs):
    self.verbose = False
    self.blurber = blurber()
    self.root_dir = None
    self.python_exe = None
    for key, value in kargs.items():
      setattr(self, key, value)
    check.check_bool(self.verbose)
    check.check_blurber(self.blurber)
    check.check_string(self.root_dir, allow_none = True)
    check.check_string(self.python_exe, allow_none = True)

  @cached_property
  def resolve_python_exe(self):
    if self.python_exe:
      return self.python_exe
    
check.register_class(pip_installer_options)
