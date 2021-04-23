#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from bes.system.log import logger
from bes.common.check import check
from bes.fs.file_find import file_find
from bes.property.cached_property import cached_property

from .vmware_error import vmware_error
from .vmware_vmx_file import vmware_vmx_file

class vmware_local_vm(object):

  logger = logger('vmware_local_vm')
  
  def __init__(self, runner, vmx_filename):
    check.check_vmware_vmrun(runner)
    check.check_string(vmx_filename)

    self._runner = runner
    self.vmx_filename = path.abspath(vmx_filename)
    self.vmx = vmware_vmx_file(self.vmx_filename)
    #command_interpreter_class = self._find_command_interpreter_class()
    #self.interpreter = command_interpreter_class()
    
  def __str__(self):
    return self.vmx_filename

  def __repr__(self):
    return self.vmx_filename
  
  @cached_property
  def nickname(self):
    return self.vmx.nickname

  @cached_property
  def uuid(self):
    return self.vmx.uuid

  @property
  def is_running(self):
    return self._runner.vm_is_running(self.vmx_filename)

  @property
  def ip_address(self):
    return self._runner.vm_get_ip_address(self.vmx_filename)

  @property
  def snapshots(self):
    return self._runner.vm_snapshots(self.vmx_filename)

  @cached_property
  def system(self):
    return self.vmx.system
  
  @cached_property
  def system_info(self):
    return self.vmx.system_info

  @property
  def display_name(self):
    return self.vmx.display_name

  @property
  def interpreter(self):
    return self.vmx.interpreter
  
#  @classmethod
#  def _find_command_interpreter_class(clazz):
#    from bes.system.host import host
#    if host.is_linux():
#      from .vmware_command_interpreter_linux import vmware_command_interpreter_linux
#      return vmware_command_interpreter_linux
#    elif host.is_macos():
#      from .vmware_command_interpreter_macos import vmware_command_interpreter_macos
#      return vmware_command_interpreter_macos
#    elif host.is_windows():
#      from .vmware_command_interpreter_windows import vmware_command_interpreter_windows
#      return vmware_command_interpreter_windows
#    else:
#      host.raise_unsupported_system()
check.register_class(vmware_local_vm)
