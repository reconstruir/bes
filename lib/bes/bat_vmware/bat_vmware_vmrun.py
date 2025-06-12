#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

import codecs
import os.path as path
import subprocess

from ..system.check import check
from bes.common.string_util import string_util
from bes.credentials.credentials import credentials
from bes.system.command_line import command_line
from bes.system.execute import execute
from bes.system.log import logger
from bes.system.os_env import os_env
from bes.text.text_line_parser import text_line_parser

from .bat_vmware_app import bat_vmware_app
from .vmware_error import vmware_error
from .vmware_power import vmware_power
from .vmware_run_program_options import vmware_run_program_options
from .bat_bat_vmware_vmx_file import bat_bat_vmware_vmx_file

class bat_vmware_vmrun(object):

  _log = logger('bat_vmware_vmrun')
  
  def __init__(self, options):
    check.check_bat_vmware_options(options)
    self._options = options

  @classmethod
  def _make_vmrun_auth_args(clazz, cred):
    args = [ '-T', bat_vmware_app.host_type() ]
    if cred:
      args.extend([ '-gu', cred.username ])
      args.extend([ '-gp', cred.password ])
    return args
    
  _run_result = namedtuple('_run_result', 'output, exit_code, args')
  def run(self, args, login_credentials = None, extra_env = None,
          no_output = False, raise_error = False, error_message = None):
    check.check_string_seq(args)
    check.check_dict(extra_env, allow_none = True)
    check.check_bool(raise_error)
    check.check_string(error_message, allow_none = True)

    self._log.log_method_d()
    exe = bat_vmware_app.vmrun_exe_path()
    auth_args = self._make_vmrun_auth_args(login_credentials)
    vmrun_args = [ exe ] + auth_args + list(args)
    self._log.log_d('run: vmrun_args={}'.format(vmrun_args))
    env = os_env.clone_current_env(d = extra_env)
    process = subprocess.Popen(vmrun_args,
                               stdout = subprocess.PIPE,
                               stderr = subprocess.STDOUT,
                               shell = False,
                               env = env)
    if no_output:
      output = None
    else:
      output_bytes, _ = process.communicate()
      output = codecs.decode(output_bytes, 'utf-8')
      
    exit_code = process.wait()
    self._log.log_d('run: exit_code={} output="{}"'.format(exit_code, output))
    if exit_code != 0 and raise_error:
      if not error_message:
        args_flat = ' '.join(vmrun_args)
        error_message = 'vmrun command failed: {}\n{}'.format(args_flat, output)
      raise vmware_error(error_message, status_code = exit_code)
    result = self._run_result(output, exit_code, vmrun_args)
    self._log.log_d('run: result: {} - {}'.format(result.exit_code, result.output))
    return result
  
  def vm_set_power_state(self, vmx_filename, state, gui = False, hard = False):
    check.check_string(vmx_filename)
    check.check_string(state)
    check.check_bool(gui)
    check.check_bool(hard)

    bat_bat_vmware_vmx_file.check_vmx_file(vmx_filename)
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
      if gui:
        args.append('gui')
      else:
        args.append('nogui')
    elif state in ( 'pause', 'unpause' ):
      pass
    return self.run(args, raise_error = False, no_output = True)

  def vm_file_copy_to(self, vmx_filename, local_filename, remote_filename, login_credentials):
    check.check_string(vmx_filename)
    check.check_string(local_filename)
    check.check_string(remote_filename)
    check.check_credentials(login_credentials)

    bat_bat_vmware_vmx_file.check_vmx_file(vmx_filename)
    self._log.log_method_d()
    args = [
      'copyFileFromHostToGuest',
      vmx_filename,
      local_filename,
      remote_filename,
    ]
    self.run(args,
             login_credentials = login_credentials,
             raise_error = True)

  def vm_file_copy_from(self, vmx_filename, remote_filename, local_filename, login_credentials):
    check.check_string(vmx_filename)
    check.check_string(remote_filename)
    check.check_string(local_filename)
    check.check_credentials(login_credentials)

    bat_bat_vmware_vmx_file.check_vmx_file(vmx_filename)
    args = [
      'copyFileFromGuestToHost',
      vmx_filename,
      remote_filename,
      local_filename,
    ]
    self.run(args,
             login_credentials = login_credentials,
             raise_error = True)

  def vm_file_exists(self, vmx_filename, remote_filename, login_credentials):
    check.check_string(vmx_filename)
    check.check_string(remote_filename)
    check.check_credentials(login_credentials)

    bat_bat_vmware_vmx_file.check_vmx_file(vmx_filename)
    args = [
      'fileExistsInGuest',
      vmx_filename,
      remote_filename,
    ]
    rv = self.run(args,
                  login_credentials = login_credentials,
                  raise_error = False)
    return rv.exit_code == 0
  
  def vm_dir_exists(self, vmx_filename, remote_directory, login_credentials):
    check.check_string(vmx_filename)
    check.check_string(remote_directory)
    check.check_credentials(login_credentials)

    bat_bat_vmware_vmx_file.check_vmx_file(vmx_filename)
    args = [
      'directoryExistsInGuest',
      vmx_filename,
      remote_directory,
    ]
    rv = self.run(args,
                  login_credentials = login_credentials,
                  raise_error = False)
    return rv.exit_code == 0
  
  def vm_dir_create(self, vmx_filename, remote_directory, login_credentials):
    check.check_string(vmx_filename)
    check.check_string(remote_directory)
    check.check_credentials(login_credentials)

    bat_bat_vmware_vmx_file.check_vmx_file(vmx_filename)
    args = [
      'createDirectoryInGuest',
      vmx_filename,
      remote_directory,
    ]
    self.run(args,
             raise_error = True,
             login_credentials = login_credentials,
             error_message = 'Failed to create dir: {}'.format(remote_directory))

  def vm_dir_delete(self, vmx_filename, remote_directory, login_credentials):
    check.check_string(vmx_filename)
    check.check_string(remote_directory)
    check.check_credentials(login_credentials)

    bat_bat_vmware_vmx_file.check_vmx_file(vmx_filename)
    args = [
      'deleteDirectoryInGuest',
      vmx_filename,
      remote_directory,
    ]
    self.run(args,
             raise_error = True,
             login_credentials = login_credentials,
             error_message = 'Failed to delete dir: {}'.format(remote_directory))

  def vm_dir_list(self, vmx_filename, remote_directory, login_credentials):
    check.check_string(vmx_filename)
    check.check_string(remote_directory)
    check.check_credentials(login_credentials)

    bat_bat_vmware_vmx_file.check_vmx_file(vmx_filename)
    args = [
      'listDirectoryInGuest',
      vmx_filename,
      remote_directory,
    ]
    rv = self.run(args,
                  raise_error = True,
                  login_credentials = login_credentials,
                  error_message = 'Failed to list dir: {}'.format(remote_directory))
    lines = self._parse_lines(rv.output)
    return sorted(lines[1:])
    
  def vm_clone(self, src_vmx_filename, dst_vmx_filename, full = False, snapshot_name = None, clone_name = None):
    check.check_string(src_vmx_filename)
    check.check_string(dst_vmx_filename)
    check.check_bool(full)
    check.check_string(snapshot_name, allow_none = True)
    check.check_string(clone_name, allow_none = True)

    bat_bat_vmware_vmx_file.check_vmx_file(src_vmx_filename)
    args = [
      'clone',
      src_vmx_filename,
      dst_vmx_filename,
      'full' if full else 'linked',
    ]
    if snapshot_name:
      args.append('-snapshot={}'.format(snapshot_name))
    if clone_name:
      args.append('-cloneName="{}"'.format(clone_name))
    return self.run(args, raise_error = True)

  def vm_stop(self, vmx_filename):
    check.check_string(vmx_filename)

    bat_bat_vmware_vmx_file.check_vmx_file(vmx_filename)
    args = [ 'stop', vmx_filename ]
    return self.run(args,
                    raise_error = True,
                    error_message = 'Failed to stop vm: {}'.format(vmx_filename))

  def vm_delete(self, vmx_filename):
    check.check_string(vmx_filename)

    bat_bat_vmware_vmx_file.check_vmx_file(vmx_filename)
    args = [ 'deleteVM', vmx_filename ]
    rv = self.run(args, raise_error = False)
    if rv.exit_code != 0:
      error_message = 'Failed to delete vm: {} - {}'.format(vmx_filename, rv.output)
      raise vmware_error(error_message, status_code = rv.exit_code)

  def vm_run_program(self, vmx_filename, program, program_args,
                     run_program_options, login_credentials):
    check.check_string(vmx_filename)
    check.check_string(program)
    check.check_string_seq(program_args)
    check.check_vmware_run_program_options(run_program_options)
    check.check_credentials(login_credentials)

    bat_bat_vmware_vmx_file.check_vmx_file(vmx_filename)
    args = [
      'runProgramInGuest',
      vmx_filename,
    ] + run_program_options.to_vmrun_command_line_args() + [
      program,
    ] + list(program_args)
    return self.run(args, login_credentials = login_credentials, raise_error = False)
  
  def vm_run_script(self, vmx_filename, interpreter_path, script_text,
                    run_program_options, login_credentials):
    check.check_string(vmx_filename)
    check.check_string(interpreter_path)
    check.check_string(script_text)
    check.check_vmware_run_program_options(run_program_options)
    check.check_credentials(login_credentials)

    bat_bat_vmware_vmx_file.check_vmx_file(vmx_filename)
    args = [
      'runScriptInGuest',
      vmx_filename,
    ] + run_program_options.to_vmrun_command_line_args() + [
      interpreter_path,
      script_text,
    ]
    return self.run(args, login_credentials = login_credentials, raise_error = False)
  
  def running_vms(self):
    self._log.log_method_d()
    args = [ 'list' ]
    rv = self.run(args, raise_error = True)
    lines = self._parse_lines(rv.output)
    return lines[1:]

  def _parse_lines(self, text):
    return text_line_parser.parse_lines(text,
                                        strip_comments = False,
                                        strip_text = True,
                                        remove_empties = True)
  
  def vm_is_running(self, vmx_filename):
    bat_bat_vmware_vmx_file.check_vmx_file(vmx_filename)

    self._log.log_method_d()
    
    running_vms = self.running_vms()
    return vmx_filename in self.running_vms()

  def vm_get_ip_address(self, vmx_filename):
    self._log.log_method_d()
    bat_bat_vmware_vmx_file.check_vmx_file(vmx_filename)

    args = [
      'getGuestIPAddress',
      vmx_filename,
    ]
    rv = self.run(args, raise_error = False)
    if rv.exit_code != 0:
      return None
    ip_address = rv.output.strip()
    if ip_address == 'unknown':
      return None
    return ip_address

  def vm_snapshot_create(self, vmx_filename, name):
    check.check_string(vmx_filename)
    check.check_string(name)

    bat_bat_vmware_vmx_file.check_vmx_file(vmx_filename)
    self._log.log_method_d()
    args = [
      'snapshot',
      vmx_filename,
      name,
    ]
    self.run(args,
             raise_error = True,
             error_message = 'Failed to create snapshot "{}" for {}'.format(name, vmx_filename))

  def vm_snapshot_delete(self, vmx_filename, name, delete_children = False):
    check.check_string(vmx_filename)
    check.check_string(name)

    bat_bat_vmware_vmx_file.check_vmx_file(vmx_filename)
    self._log.log_method_d()
    args = [
      'deleteSnapshot',
      vmx_filename,
      name,
    ]
    if delete_children:
      args.append('andDeleteChildren')
    self.run(args,
             raise_error = True,
             error_message = 'Failed to delete snapshot "{}" for {}'.format(name, vmx_filename))

  def vm_snapshots(self, vmx_filename, tree = False):
    check.check_string(vmx_filename)
    check.check_bool(tree)

    bat_bat_vmware_vmx_file.check_vmx_file(vmx_filename)
    self._log.log_method_d()
    args = [
      'listSnapshots',
      vmx_filename,
    ]
    rv = self.run(args,
                  raise_error = True,
                  error_message = 'Failed to list snapshots for {}'.format(vmx_filename))
    lines = text_line_parser.parse_lines(rv.output,
                                         strip_comments = False,
                                         strip_text = True,
                                         remove_empties = True)
    return lines[1:]
  
check.register_class(bat_vmware_vmrun)
