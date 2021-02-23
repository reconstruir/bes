#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path

from bes.common.check import check
from bes.common.string_util import string_util
from bes.credentials.credentials import credentials
from bes.system.command_line import command_line
from bes.system.log import logger
from bes.text.text_line_parser import text_line_parser

from .vmware_app import vmware_app
from .vmware_error import vmware_error
from .vmware_power import vmware_power
from .vmware_run_program_options import vmware_run_program_options
from .vmware_vmrun_exe import vmware_vmrun_exe
from .vmware_vmx_file import vmware_vmx_file

class vmware_vmrun(object):

  _log = logger('vmware_vmrun')
  
  def __init__(self, login_credentials = None):
    check.check_credentials(login_credentials, allow_none = True)

    self._login_credentials = login_credentials
    self._app = vmware_app()
    self._auth_args = self._make_vmrun_auth_args(self._app, self._login_credentials)

  def run(self, args, extra_env = None, cwd = None,
          non_blocking = False, shell = False, raise_error = False,
          error_message = None, parse_args = True):
    check.check_string_seq(args)
    check.check_dict(extra_env, allow_none = True)

    if parse_args:
      parsed_args = command_line.parse_args(args)
    else:
      parsed_args = args[:]
      
    vmrun_exe_args = self._auth_args + parsed_args
    self._log.log_d('run: vm_run_program: vmrun_exe_args={}'.format(vmrun_exe_args))
    return vmware_vmrun_exe.call_vmrun(vmrun_exe_args,
                                       extra_env = extra_env,
                                       cwd = cwd,
                                       non_blocking = non_blocking,
                                       shell = shell,
                                       raise_error = raise_error)

  def vm_set_power_state(self, vmx_filename, state, gui = False, hard = False):
    check.check_string(vmx_filename)
    check.check_string(state)
    check.check_bool(gui)
    check.check_bool(hard)

    vmware_vmx_file.check_vmx_file(vmx_filename)
    vmware_power.check_state(state)
    
    args = [ state, vmx_filename ]
    if state in ( 'start',  ):
      if gui:
        args.append('gui')
      else:
        args.append('nogui')
    elif state in ( 'stop', 'reset', 'suspend' ):
      if hard:
        args.append('hard')
      else:
        args.append('soft')
    elif state in ( 'pause', 'unpause' ):
      pass
    return self.run(args, raise_error = True)

  def vm_file_copy_to(self, vmx_filename, local_filename, remote_filename):
    check.check_string(vmx_filename)
    check.check_string(local_filename)
    check.check_string(remote_filename)

    vmware_vmx_file.check_vmx_file(vmx_filename)
    args = [
      'copyFileFromHostToGuest',
      vmx_filename,
      local_filename,
      remote_filename,
    ]
    return self.run(args, raise_error = True)

  def vm_file_copy_from(self, vmx_filename, remote_filename, local_filename):
    check.check_string(vmx_filename)
    check.check_string(remote_filename)
    check.check_string(local_filename)

    vmware_vmx_file.check_vmx_file(vmx_filename)
    args = [
      'copyFileFromGuestToHost',
      vmx_filename,
      remote_filename,
      local_filename,
    ]
    return self.run(args, raise_error = True)

  def vm_clone(self, src_vmx_filename, dst_vmx_filename, full = False, snapshot_name = None, clone_name = None):
    check.check_string(src_vmx_filename)
    check.check_string(dst_vmx_filename)
    check.check_bool(full)
    check.check_string(snapshot_name, allow_none = True)
    check.check_string(clone_name, allow_none = True)

    vmware_vmx_file.check_vmx_file(src_vmx_filename)
    args = [
      'clone',
      src_vmx_filename,
      dst_vmx_filename,
      'full' if full else 'linked',
    ]
    if snapshot_name:
      args.append('-snapshot="{}"'.format(snapshot_name))
    if clone_name:
      args.append('-cloneName="{}"'.format(clone_name))
    return self.run(args, raise_error = True)

  def vm_stop(self, vmx_filename):
    check.check_string(vmx_filename)

    vmware_vmx_file.check_vmx_file(vmx_filename)
    args = [ 'stop', vmx_filename ]
    return self.run(args,
                    raise_error = True,
                    error_message = 'Failed to stop vm: {}'.format(vmx_filename))

  def vm_delete(self, vmx_filename):
    check.check_string(vmx_filename)

    vmware_vmx_file.check_vmx_file(vmx_filename)
    args = [ 'deleteVM', vmx_filename ]
    return self.run(args,
                    raise_error = True,
                    error_message = 'Failed to delete vm: {}'.format(vmx_filename))

  def vm_delete(self, vmx_filename):
    check.check_string(vmx_filename)

    vmware_vmx_file.check_vmx_file(vmx_filename)
    args = [ 'deleteVM', vmx_filename ]
    return self.run(args,
                    raise_error = True,
                    error_message = 'Failed to delete vm: {}'.format(vmx_filename))

  def vm_run_program(self, vmx_filename, program, run_program_options):
    check.check_string(vmx_filename)
    #check.check_string(program)
    check.check_vmware_run_program_options(run_program_options)

    vmware_vmx_file.check_vmx_file(vmx_filename)
    program_args = command_line.parse_args(program)
    args = [
      'runProgramInGuest',
      vmx_filename,
    ] + run_program_options.to_vmrun_command_line_args() + program_args
    return self.run(args, raise_error = False)
  
  def vm_run_script(self, vmx_filename, interpreter_path, script, run_program_options):
    check.check_string(vmx_filename)
    check.check_string(interpreter_path)
    check.check_string(script)
    check.check_vmware_run_program_options(run_program_options)

    vmware_vmx_file.check_vmx_file(vmx_filename)
    args = [
      'runScriptInGuest',
      vmx_filename,
    ] + run_program_options.to_vmrun_command_line_args() + [
      interpreter_path,
      '"{}"'.format(script),
    ]
    return self.run(args, raise_error = False, parse_args = False)
  
  def running_vms(self):
    args = [ 'list' ]
    rv = self.run(args, raise_error = True)
    lines = text_line_parser.parse_lines(rv.stdout,
                                         strip_comments = False,
                                         strip_text = True,
                                         remove_empties = True)
    return lines[1:]

  def vm_is_running(self, vmx_filename):
    vmware_vmx_file.check_vmx_file(vmx_filename)

    running_vms = self.running_vms()
    return vmx_filename in self.running_vms()
  
  @classmethod
  def _make_vmrun_auth_args(clazz, app, cred):
    args = [ '-T', app.host_type() ]
    if cred:
      args.extend([ '-gu', cred.username ])
      args.extend([ '-gp', cred.password ])
    return args
