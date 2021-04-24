#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from bes.common.check import check
from bes.fs.file_find import file_find
from bes.property.cached_property import cached_property
from bes.system.log import logger

from .vmware_command_interpreter_manager import vmware_command_interpreter_manager
from .vmware_error import vmware_error
from .vmware_run_program_options import vmware_run_program_options
from .vmware_vmx_file import vmware_vmx_file

class vmware_local_vm(object):

  _log = logger('vmware_local_vm')
  
  def __init__(self, runner, vmx_filename):
    check.check_vmware_vmrun(runner)
    check.check_string(vmx_filename)

    self._runner = runner
    self.vmx_filename = path.abspath(vmx_filename)
    self.vmx = vmware_vmx_file(self.vmx_filename)
    
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

  def can_run_programs(self, run_program_options = None):
    'Return True if the vm can run programs'
    check.check_vmware_run_program_options(run_program_options, allow_none = True)
    
    run_program_options = run_program_options or vmware_run_program_options()

    self._log.log_method_d()
    
    if not self.ip_address:
      return False
    cim = vmware_command_interpreter_manager.instance()
    default_interpreter = cim.find_default_interpreter(self.system)

    # "exit 0" works on all the default interpreters for both windows and unix
    command = default_interpreter.build_command('exit 0')
    
    rv = self._runner.vm_run_script(self.vmx_filename,
                                    command.interpreter_path,
                                    command.script_text,
                                    run_program_options)
    self._log.log_d('can_run_programs: exit_code={}'.format(rv.exit_code))
    return rv.exit_code == 0

  def run_script(self,
                 script,
                 run_program_options = None,
                 interpreter_name = None):
    check.check_string(script)
    check.check_vmware_run_program_options(run_program_options, allow_none = True)
    check.check_string(interpreter_name, allow_none = True)

    run_program_options = run_program_options or vmware_run_program_options()

    self._log.log_method_d()

    cim = vmware_command_interpreter_manager.instance()
    interpreter = cim.resolve_interpreter(self.system, interpreter_name)
    self._log.log_d('run_script: interpreter={}'.format(interpreter))
    command = interpreter.build_command(script)
    self._log.log_d('run_script: command={}'.format(command))

    rv = self._runner.vm_run_script(self.vmx_filename,
                                    command.interpreter_path,
                                    command.script_text,
                                    run_program_options)
    return rv
  
check.register_class(vmware_local_vm)
