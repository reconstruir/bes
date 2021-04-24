#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common.check import check
from bes.script.blurber import blurber

from .pip_error import pip_error

class pip_project_options(object):
  
  def __init__(self, *args, **kargs):
    self.debug = False
    self.verbose = False
    self.blurber = blurber()
    self.root_dir = None
    self.python_version = None
    self.name = None
    for key, value in kargs.items():
      setattr(self, key, value)
    check.check_bool(self.debug)
    check.check_bool(self.verbose)
    check.check_blurber(self.blurber)
    check.check_string(self.root_dir, allow_none = True)
    check.check_string(self.python_version, allow_none = True)
    check.check_string(self.name, allow_none = True)

  def resolve_python_exe(self):
    from bes.python.python_exe import python_exe
    if not self.python_version:
      exe = python_exe.default_exe()
      if not exe:
        raise pip_error('No default python found')
    else:
      exe = python_exe.find_version(self.python_version)
      if not exe:
        raise pip_error('No python found for version "{}"'.format(self.python_version))
    return exe

  def resolve_root_dir(self):
    if self.root_dir:
      return self.root_dir
    import os
    import os.path as path
    return path.join(os.getcwd(), 'BES_PIP_ROOT')
    
check.register_class(pip_project_options)
