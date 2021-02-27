#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple
import os.path as path
import subprocess

from bes.common.check import check
from bes.common.string_util import string_util
from bes.credentials.credentials import credentials
from bes.system.command_line import command_line
from bes.system.execute import execute
from bes.system.log import logger
from bes.system.os_env import os_env
from bes.text.text_line_parser import text_line_parser

from .vmware_app import vmware_app
from .vmware_error import vmware_error
from .vmware_power import vmware_power
from .vmware_run_program_options import vmware_run_program_options
from .vmware_vmx_file import vmware_vmx_file

class vmware_vmrun(object):

  _log = logger('vmware_vmrun')
  
  def __init__(self, login_credentials = None):
    check.check_credentials(login_credentials, allow_none = True)

    self._login_credentials = login_credentials
    self._auth_args = self._make_vmrun_auth_args(self._login_credentials)

  _run_result = namedtuple('_run_result', 'output, exit_code, args')
  def run(self, args, extra_env = None,
          raise_error = False, error_message = None):
    check.check_string_seq(args)
    check.check_dict(extra_env, allow_none = True)
    check.check_bool(raise_error)
    check.check_string(error_message, allow_none = True)

    self._log.log_method_d()
    exe = vmware_app.vmrun_exe_path()
    vmrun_args = [ exe ] + self._auth_args + list(args)
    self._log.log_d('run: vmrun_args={}'.format(vmrun_args))

    env = os_env.clone_current_env(d = extra_env)

    try:
      self._log.log_d('run: calling: {}'.format(' '.join(vmrun_args)))
      output = subprocess.check_output(vmrun_args,
                                       stderr = subprocess.STDOUT,
                                       shell = False,
                                       env = env)
    except subprocess.CalledProcessError as ex:
      exit_code = ex.returncode
      self._log.log_d('run: caught exception: {} - {}'.format(str(ex), exit_code))
      output = ex.output
      if raise_error:
        if not error_message:
          args_flat = ' '.join(vmrun_args)
          error_message or 'vmrun command failed: {}\n{}'.format(args_flat, output)
        raise vmware_error(error_message, status_code = exit_code)
    else:
      exit_code = 0
    result = self._run_result(output, exit_code, vmrun_args)
    self._log.log_d('run: result: {} - {}'.format(result.exit_code, result.output))
    return result

  def vm_set_power_state(self, vmx_filename, state, gui = False, hard = False):
    check.check_string(vmx_filename)
    check.check_string(state)
    check.check_bool(gui)
    check.check_bool(hard)

    vmware_vmx_file.check_vmx_file(vmx_filename)
    vmware_power.check_state(state)

    self._log.log_method_d()
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
    self._log.log_method_d()
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

  def vm_file_exists(self, vmx_filename, remote_filename):
    check.check_string(vmx_filename)
    check.check_string(remote_filename)

    vmware_vmx_file.check_vmx_file(vmx_filename)
    args = [
      'fileExistsInGuest',
      vmx_filename,
      remote_filename,
    ]
    rv = self.run(args, raise_error = False)
    return rv.exit_code == 0

  def vm_directory_exists(self, vmx_filename, remote_directory):
    check.check_string(vmx_filename)
    check.check_string(remote_directory)

    vmware_vmx_file.check_vmx_file(vmx_filename)
    args = [
      'directoryExistsInGuest',
      vmx_filename,
      remote_directory,
    ]
    rv = self.run(args, raise_error = False)
    return rv.exit_code == 0
  
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

  def vm_run_program(self, vmx_filename, program, program_args, run_program_options):
    check.check_string(vmx_filename)
    check.check_string(program)
    check.check_string_seq(program_args)
    check.check_vmware_run_program_options(run_program_options)

    vmware_vmx_file.check_vmx_file(vmx_filename)
    args = [
      'runProgramInGuest',
      vmx_filename,
    ] + run_program_options.to_vmrun_command_line_args() + [
      program,
    ] + list(program_args)
    return self.run(args, raise_error = False)
  
  def vm_run_script(self, vmx_filename, interpreter_path, script_text, run_program_options):
    check.check_string(vmx_filename)
    check.check_string(interpreter_path)
    check.check_string(script_text)
    check.check_vmware_run_program_options(run_program_options)

    vmware_vmx_file.check_vmx_file(vmx_filename)
    args = [
      'runScriptInGuest',
      vmx_filename,
    ] + run_program_options.to_vmrun_command_line_args() + [
      interpreter_path,
      script_text,
    ]
    return self.run(args, raise_error = False)
  
  def running_vms(self):
    self._log.log_method_d()
    args = [ 'list' ]
    rv = self.run(args, raise_error = True)
    lines = text_line_parser.parse_lines(rv.output,
                                         strip_comments = False,
                                         strip_text = True,
                                         remove_empties = True)
    return lines[1:]

  def vm_is_running(self, vmx_filename):
    self._log.log_method_d()
    vmware_vmx_file.check_vmx_file(vmx_filename)

    running_vms = self.running_vms()
    return vmx_filename in self.running_vms()
  
  @classmethod
  def _make_vmrun_auth_args(clazz, cred):
    args = [ '-T', vmware_app.host_type() ]
    if cred:
      args.extend([ '-gu', cred.username ])
      args.extend([ '-gp', cred.password ])
    return args
