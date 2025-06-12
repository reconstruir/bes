#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from .vmware_command_interpreter_unix import vmware_command_interpreter_unix
from .vmware_error import vmware_error

class vmware_command_interpreter_macos(vmware_command_interpreter_unix):
  pass
