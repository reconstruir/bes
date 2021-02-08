#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple
import os.path as path

from bes.system.log import logger
from bes.system.command_line import command_line
from bes.system.host import host
from bes.common.check import check
from bes.fs.file_find import file_find
from bes.fs.file_util import file_util
from bes.fs.temp_file import temp_file
from bes.archive.archiver import archiver

from .vmware_app import vmware_app
from .vmware_error import vmware_error
from .vmware_local_vm import vmware_local_vm
from .vmware_preferences import vmware_preferences
from .vmware_session import vmware_session
from .vmware_vmrun_exe import vmware_vmrun_exe
from .vmware_vmx_file import vmware_vmx_file

class vmware(object):

  _log = logger('vmware')
  
  def __init__(self, vm_dir = None):
    self._preferences_filename = vmware_preferences.default_preferences_filename()
    self._preferences = vmware_preferences(self._preferences_filename)
    self._vm_dir = vm_dir
    if not self._vm_dir:
      self._vm_dir = self._default_vm_dir()
    if not self._vm_dir:
      raise vmware_error('no vm_dir given and no default configured in {}'.format(self._preferences_filename))
    self.local_vms = {}
    vmx_files = file_find.find(self._vm_dir, relative = False, match_patterns = [ '*.vmx' ])
    for vmx_filename in vmx_files:
      local_vm = vmware_local_vm(vmx_filename)
      self.local_vms[local_vm.nickname] = local_vm
    self._session = None
    self._app = vmware_app()

  def _default_vm_dir(self):
    if self._preferences.has_value('prefvmx.defaultVMPath'):
      return self._preferences.get_value('prefvmx.defaultVMPath')
    return None

  @property
  def session(self):
    if not self._session:
      self._session = vmware_session()
      self._session.start()
    return self._session

  def vm_run_program(self, vm_id, username, password, program,
                     copy_vm, dont_ensure):
    check.check_string(vm_id)
    check.check_string(username)
    check.check_string(password)
    check.check_string_seq(program)
    check.check_bool(copy_vm)
    check.check_bool(dont_ensure)

    vmx_filename = self._resolve_vmx_filename(vm_id)
    self._log.log_d('vm_run_program: vm_id={} vmx_filename={}'.format(vm_id, vmx_filename))

    self._ensure_running_if_needed(vm_id, dont_ensure)

    program_args = command_line.parse_args(program)
    args = self._authentication_args(username = username, password = password) + [
      'runProgramInGuest',
      vmx_filename,
      '-interactive',
    ] + program_args
    self._log.log_d('vm_run_program: args={}'.format(args))
    rv = vmware_vmrun_exe.call_vmrun(args)
    return rv

  def vm_run_package(self, vm_id, username, password, package_dir,
                     entry_command, entry_command_args, copy_vm,
                     dont_ensure, output_filename, tail_log,
                     debug, tty):
    check.check_string(vm_id)
    check.check_string(username)
    check.check_string(password)
    check.check_string(package_dir)
    check.check_string(entry_command)
    check.check_string_seq(entry_command_args)
    check.check_bool(copy_vm)
    check.check_bool(dont_ensure)
    check.check_string(output_filename, allow_none = True)
    check.check_bool(tail_log)
    check.check_bool(debug)
    check.check_string(tty, allow_none = True)

    if not path.isdir(package_dir):
      raise vmware_error('package_dir not found or not a dir: "{}"'.format(package_dir))

    vmx_filename = self._resolve_vmx_filename(vm_id)
    self._log.log_d('vm_run_package: vm_id={} vmx_filename={}'.format(vm_id, vmx_filename))

    self._ensure_running_if_needed(vm_id, dont_ensure)

    tmp_dir_local = temp_file.make_temp_dir(suffix = '-run_package.dir', delete = not debug)
    if debug:
      print('tmp_dir_local={}'.format(tmp_dir_local))

    tmp_remote_dir = path.join('/tmp', path.basename(tmp_dir_local))
    self._log.log_d('      vm_run_package: tmp_remote_dir={}'.format(tmp_remote_dir))

    rmdir_cmd = '/bin/rm -rf {}'.format(tmp_remote_dir)
    mkdir_cmd = '/bin/mkdir -p {}'.format(tmp_remote_dir)
    rv = self.vm_run_program(vm_id, username, password, rmdir_cmd, False, False)
    if rv.exit_code != 0:
      raise vmware_error('vm_run_package: failed to: "{}"'.format(rmdir_cmd))
    self.vm_run_program(vm_id, username, password, mkdir_cmd, False, False)
    if rv.exit_code != 0:
      raise vmware_error('vm_run_package: failed to: "{}"'.format(mkdir_cmd))
    
    tmp_package = self._make_tmp_file_pair(tmp_dir_local, 'package.zip')
    tmp_caller_script = self._make_tmp_file_pair(tmp_dir_local, 'caller_script.py')
    tmp_output_log = self._make_tmp_file_pair(tmp_dir_local, 'output.log')

    archiver.create(tmp_package.local, package_dir)
    file_util.save(tmp_caller_script.local,
                   content = self._RUN_PACKAGE_CALLER_PYTHON,
                   mode = 0o0755)
    self._log.log_d('      vm_run_package: tmp_package={}'.format(tmp_package))
    self._log.log_d('      vm_run_package: tmp_caller_script={}'.format(tmp_caller_script))
    self._log.log_d('      vm_run_package: tmp_output_log={}'.format(tmp_output_log))
    
    self.vm_copy_to(vm_id, username, password, tmp_package.local, tmp_package.remote, True)
    self.vm_copy_to(vm_id, username, password, tmp_caller_script.local, tmp_caller_script.remote, True)

    parsed_entry_command_args = command_line.parse_args(entry_command_args)
    debug_args = []
    if debug:
      debug_args.append('--debug')
    if tty:
      debug_args.extend([ '--tty', tty ])
      
    caller_args = [ tmp_caller_script.remote ] + debug_args + [
      tmp_package.remote,      
      entry_command,
      tmp_output_log.remote,      
    ] + parsed_entry_command_args
    args = self._authentication_args(username = username, password = password) + [
      'runProgramInGuest',
      vmx_filename,
      '-interactive',
    ] + caller_args
    self._log.log_d('vm_run_package: caller_args={}'.format(caller_args))
    rv = vmware_vmrun_exe.call_vmrun(args)

    self.vm_copy_from(vm_id, username, password, tmp_output_log.remote, tmp_output_log.local, True)

    with file_util.open_with_default(filename = output_filename) as f:
      log_content = file_util.read(tmp_output_log.local, codec = 'utf-8')
      f.write(log_content)
    
    return rv

  _tmp_file_pair = namedtuple('_tmp_file_pair', 'local, remote')
  def _make_tmp_file_pair(self, tmp_dir_local, name):
    local = path.join(tmp_dir_local, name)
    remote = path.join('/tmp', path.basename(tmp_dir_local), name)
    return self._tmp_file_pair(local, remote)
    
  def _make_temp_tmp_filename(self, local_tmp_filename):
    tmp_basename = path.basename(local_tmp_filename)
    tmp_remote_filename = path.join('/tmp', tmp_basename)
    return tmp_remote_filename
  
  def _ensure_running_if_needed(self, vm_id, dont_ensure):
    if dont_ensure:
      self._log.log_d('_ensure_running_if_needed: doing nothing cause dont_ensure is True')
      return
    
    resolved_vm_id = self.session.resolve_vm_id(vm_id)
    self._log.log_d('_ensure_running_if_needed: ensuring vm {}:{} is running'.format(vm_id, resolved_vm_id))
    self._app.ensure_running()
  
  def vm_clone(self, vm_id, dst_vmx_filename, full = False, snapshot_name = None, clone_name = None):
    check.check_string(vm_id)
    check.check_string(dst_vmx_filename)
    check.check_bool(full)
    check.check_string(snapshot_name, allow_none = True)
    check.check_string(clone_name, allow_none = True)
    
    src_vmx_filename = self._resolve_vmx_filename(vm_id)
    if path.exists(dst_vmx_filename):
      raise vmware_error('dst_vmx_filename already exists: "{}"'.format(dst_vmx_filename))
    
    args = self._authentication_args() + [
      'clone',
      src_vmx_filename,
      dst_vmx_filename,
      'full' if full else 'linked',
    ]
    if snapshot_name:
      args.append('-snapshot="{}"'.format(snapshot_name))
    if clone_name:
      args.append('-cloneName="{}"'.format(clone_name))
    rv = vmware_vmrun_exe.call_vmrun(args)
    return rv
  
  def _resolve_vmx_filename(self, vm_id):
    return self._resolve_vmx_filename_local_vms(vm_id) or self._resolve_vmx_filename_rest_vms(vm_id)
  
  def _resolve_vmx_filename_local_vms(self, vm_id):
    if vmware_vmx_file.is_vmx_file(vm_id):
      return vm_id
    for nickname, vm in self.local_vms.items():
      if vm_id in [ nickname, vm.vmx_filename ]:
        return vm.vmx_filename
    return None

  def _resolve_vmx_filename_rest_vms(self, vm_id):
    rest_vms = self.session.client.vms()
    for vm in rest_vms:
      if vm_id == vm.vm_id:
        return vm.path
    return None

  def _authentication_args(self, username = None, password = None):
    args = [ '-T', self._app.host_type() ]
    if username:
      args.extend([ '-gu', username ])
    if password:
      args.extend([ '-gp', password ])
    return args

  def vm_copy_to(self, vm_id, username, password, local_filename, remote_filename, dont_ensure):
    check.check_string(vm_id)
    check.check_string(username)
    check.check_string(password)
    check.check_string(local_filename)
    check.check_string(remote_filename)
    check.check_bool(dont_ensure)

    src_vmx_filename = self._resolve_vmx_filename(vm_id)
    
    local_filename = path.abspath(local_filename)
    if not path.isfile(local_filename):
      raise vmware_error('local filename not found: "{}"'.format(local_filename))
      
    args = self._authentication_args(username = username, password = password) + [
      'copyFileFromHostToGuest',
      src_vmx_filename,
      local_filename,
      remote_filename,
    ]
    vmware_vmrun_exe.call_vmrun(args, raise_error = True)

  def vm_copy_from(self, vm_id, username, password, remote_filename, local_filename, dont_ensure):
    check.check_string(vm_id)
    check.check_string(username)
    check.check_string(password)
    check.check_string(remote_filename)
    check.check_string(local_filename)
    check.check_bool(dont_ensure)

    src_vmx_filename = self._resolve_vmx_filename(vm_id)
    
    args = self._authentication_args(username = username, password = password) + [
      'copyFileFromGuestToHost',
      src_vmx_filename,
      remote_filename,
      local_filename,
    ]
    file_util.remove(local_filename)
    vmware_vmrun_exe.call_vmrun(args, raise_error = True)
    assert path.isfile(local_filename)

  _RUN_PACKAGE_CALLER_BASH = '''\
#!/bin/bash

function _log()
{
  # uncomment this to log the actions of this caller script itself to a tty or file on the guest
  return 0
  local _LOG_DEST=/dev/ttys000
  local _name="$(basename ${BASH_SOURCE[0]})"
  printf "${_name}: "${1+"$@"} >& ${_LOG_DEST}
  printf "\n\n" >& ${_LOG_DEST}
  return 0
}

_log "script: ${BASH_SOURCE[0]}"
set -e -x
_log "after set"
function main()
{
  _log "main starts"
  local _name="$(basename ${BASH_SOURCE[0]})"
  _log "_name=${_name}"
  _log "args before: $*"
  if [[ $# < 3 ]]; then
    _log "bad args"
    echo "usage: ${_name} package_zip entry_command output_log"
    _log "return 1"
    return 1
  fi
  _log "num args check passed"
  local _package_zip="${1}"
  shift
  local _entry_command="${1}"
  shift
  local _output_log="${1}"
  shift
  _log "args after: $*"
  _log "_package_zip=${_package_zip} _entry_command=${_entry_command} _output_log=${_output_log}"
  local _tmp="$(mktemp -d /tmp/${_name}.XXXXXX)"
  rm -rf ${_tmp}
  mkdir -p ${_tmp}
  cd ${_tmp}
  unzip "${_package_zip}"
  local _output_log_dir=$(dirname "${_output_log}")
  mkdir -p "${_output_log_dir}"
  _log "calling command: ${_entry_command} $* >& ${_output_log}"
  ( ./"${_entry_command}" $* >& ${_output_log} )
  local _exit_code=$?
  _log "after command _exit_code=${_exit_code}"
  return ${_exit_code}
}

_log "before main"
main ${1+"$@"}
_log "after main"
'''

  _RUN_PACKAGE_CALLER_PYTHON = r'''#!/usr/bin/env python

import argparse
import os
import os.path as path
import platform
import sys
import tarfile
import tempfile
import zipfile
import subprocess

class package_caller(object):

  def __init__(self):
    pass
  
  def main(self):
    p = argparse.ArgumentParser()
    p.add_argument('-v', '--verbose', action = 'store_true', default = False,
                   help = 'Verbose log output [ False ]')
    p.add_argument('--debug', action = 'store_true', default = False,
                   help = 'Debug mode.  Save temp files and log the script itself [ False ]')
    p.add_argument('--tty', action = 'store', default = None,
                   help = 'tty to log to in debug mode [ False ]')
    p.add_argument('package_zip', action = 'store', default = None,
                   help = 'The package []')
    p.add_argument('entry_command', action = 'store', default = None,
                   help = 'The entry command []')
    p.add_argument('output_log', action = 'store', default = None,
                   help = 'The output log file []')
    p.add_argument('entry_command_args', action = 'store', default = [], nargs = '*',
                   help = 'Optional entry command args [ ]')
    args = p.parse_args()
    with open(args.output_log, 'w') as fout:
      for key, value in sorted(args.__dict__.items()):
        fout.write('args: {}={}\n'.format(key, value))
      fout.flush()
    self._debug = args.debug
    self._name = path.basename(sys.argv[0])
    self._console_device = args.tty or self._find_console_device()
    with open('/dev/ttys000', 'w') as cccc:
      cccc.write('{}\n'.format(args.tty))
      cccc.flush()
    tmp_dir = path.join(path.dirname(args.package_zip), 'work')
    self._log('tmp_dir={}'.format(tmp_dir))

    self._log('package_zip={} entry_command={} output_log={}'.format(args.package_zip,
                                                                     args.entry_command,
                                                                     args.output_log))

    self._unpack_package(args.package_zip, tmp_dir)
    exit_code = self._execute(tmp_dir,
                              args.entry_command,
                              args.output_log,
                              args.entry_command_args)
    return exit_code
    
  def _execute(self, dest_dir, command, output_log, entry_command_args):
    entry_command_args = entry_command_args or []
    stdout_pipe = subprocess.PIPE
    stderr_pipe = subprocess.STDOUT
    command_abs = path.join(dest_dir, command)
    if not path.isfile(command_abs):
      raise IOError('entry command not found: "{}"'.format(command_abs))
    args = [ command_abs ] + entry_command_args
    self._log('args={} cwd={}'.format(args, dest_dir))
    os.chmod(command_abs, 0o0755)

    poto = open('/Users/ramiro/poto.log', 'w')
    poto.write('before\n')
    poto.flush()
    process = subprocess.Popen(args,
                               stdout = stdout_pipe,
                               stderr = stderr_pipe,
                               shell = False,
                               cwd = dest_dir,
                               universal_newlines = True)
    poto.write('after 1\n')
    poto.flush()
    output = process.communicate()
    poto.write('after 2\n')
    poto.flush()
    exit_code = process.wait()
    poto.write('after 3: exit_code={}\n'.format(exit_code))
    poto.flush()
    self._mkdir(path.dirname(output_log))
    stdout = output[0]
    poto.write('after 4: stdout={}\n'.format(stdout))
    poto.flush()
    with open('/tmp/xxx.log', 'w') as ffff:
      ffff.write(output_log + '\n')
      ffff.flush()
    with open(output_log, 'a') as fout:
      fout.write(stdout)
      fout.flush()
    with open('/dev/ttys000', 'w') as caca:
      caca.write('finished')
      caca.flush()
    poto.write('after 5\n')
    poto.flush()
    return exit_code

  @classmethod
  def _mkdir(clazz, p):
    if path.isdir(p):
      return
    os.makedirs(p)
  
  def _unpack_package_zip(self, package_zip, dest_dir):
    with zipfile.ZipFile(package_zip, mode = 'r') as f:
      f.extractall(path = dest_dir)

  def _unpack_package_tar(self, package_tar, dest_dir):
    with tarfile.open(package_tar, mode = 'r') as f:
      f.extractall(path = dest_dir)

  def _unpack_package(self, package, dest_dir):
    if zipfile.is_zipfile(package):
      self._unpack_package_zip(package, dest_dir)
    elif tarfile.is_tarfile(package):
      self._unpack_package_tar(package, dest_dir)
    else:
      raise RuntimeError('unknown archive type: "{}"'.format(package))
      
  def _log(self, message):
    if not self._debug:
      return
    s = '{}: {}\n'.format(self._name, message)
    with open(self._console_device, 'w') as f:
      f.write(s)
      f.flush()

  @classmethod
  def _find_console_device(clazz):
    system = platform.system()
    if system == 'Windows':
      return 'con:'
    elif system == 'Darwin':
      return '/dev/tty'
    elif system == 'Linux':
      return '/dev/console'
    else:
      raise RuntimeError('unknown platform: "{}"'.format(system))

  @classmethod
  def run(clazz):
    raise SystemExit(package_caller().main())

if __name__ == '__main__':
  package_caller.run()
'''  
