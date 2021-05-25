#!/usr/bin/env python

import argparse
import os
import os.path as path
import platform
import sys
import tarfile
import tempfile
import zipfile
import subprocess

from bes.archive.archiver import archiver
from bes.fs.temp_file import temp_file
from bes.fs.tar_util import tar_util
from bes.fs.file_util import file_util
from bes.system.log import logger
from bes.system.execute import execute
from bes.system.os_env import os_env

from bes.vmware.vmware_options_cli_args import vmware_options_cli_args

class vmware_tester(object):

  _log = logger('vmware_tester')

  def __init__(self):
    pass

  def main(self):
    p = argparse.ArgumentParser()
    vmware_options_cli_args.add_arguments(p)
    p.add_argument('--tail-log', action = 'store_true', default = False,
                   help = 'Tail the log [ False ]')
    p.add_argument('--dir', action = 'store', default = os.getcwd(),
                   dest = 'source_dir',
                   help = 'Directory to use for the package [ False ]')
    p.add_argument('-o', '--output', action = 'store', default = None,
                   dest = 'output_filename',
                   help = 'Output the log to filename instead of stdout [ False ]')
    p.add_argument('--clone-vm', action = 'store_true', default = False,
                   help = 'Run programs in a clone of the vm [ False ]')
    p.add_argument('vm_id', action = 'store', default = None,
                   help = 'The vmware vmx filename for the vm to test [ None ]')
    p.add_argument('entry_command_args', action = 'store', default = [], nargs = '*',
                   help = 'Optional entry command args [ ]')
    args = p.parse_args()

    self._debug = args.debug
    self._name = path.basename(sys.argv[0])
    tmp_dir = tempfile.mkdtemp()

    tar_util.copy_tree(args.source_dir,
                       tmp_dir,
                       excludes = self._PACKAGE_EXCLUDES)
    entry_command_path = path.join(tmp_dir, self._ENTRY_COMMAND_FILENAME)
    file_util.save(entry_command_path, content = self._ENTRY_COMMAND_CONTENT)

    env = os_env.clone_current_env(d = {
      'xBES_LOG': 'vmware=debug',
    })

    extra_args = []
    if args.debug:
      extra_args.append('--debug')
    if args.tty:
      extra_args.extend([ '--tty', tty ])
    if args.tail_log:
      extra_args.append('--tail-log')
    if args.clone_vm:
      extra_args.append('--clone-vm')
    if args.output_filename:
      extra_args.extend([ '--output', args.output_filename ])
    if args.config_filename:
      print(config_filename)
      extra_args.extend([ '--config', args.config_filename ])
    if args.vmrest_username:
      extra_args.extend([ '--vmrest-username', args.vmrest_username ])
    if args.vmrest_password:
      extra_args.extend([ '--vmrest-password', args.vmrest_password ])
    if args.vmrest_port:
      extra_args.extend([ '--vmrest-port', str(args.vmrest_port) ])
    if args.login_username:
      extra_args.extend([ '--login-username', args.login_username ])
    if args.login_password:
      extra_args.extend([ '--login-password', args.login_password ])
    cmd = [
      'bin/best.py',
      'vmware', 'vm_run_package',
    ] + extra_args + [
      args.vm_id,
      tmp_dir,
      self._ENTRY_COMMAND_FILENAME,
    ] + args.entry_command_args
    self._log.log_d('cmd={}'.format(' '.join([ str(x) for x in cmd ])))
    rv = execute.execute(cmd,
                         env = env,
                         raise_error = False,
                         shell = False,
                         non_blocking = True,
                         stderr_to_stdout = True)
    if rv.exit_code != 0:
      print(rv.stdout)
    return rv.exit_code
    
  @classmethod
  def run(clazz):
    raise SystemExit(vmware_tester().main())

  _PACKAGE_EXCLUDES = [
    '.git*',
    '*~',
    '*~',
    '#*',
    '.#*',
  ]

  _ENTRY_COMMAND_FILENAME = 'entry-command.sh'
      
  _ENTRY_COMMAND_CONTENT = r'''#!/bin/bash
set -e
export PYTHONPATH=$(pwd)/lib
python3 ./bin/bes_test.py --dont-hack-env --root-dir . ${1+"$@"}
exit $?
'''
  
if __name__ == '__main__':
  vmware_tester.run()
