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

class vmware_tester(object):

  _log = logger('vmware_tester')

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
    p.add_argument('--dir', action = 'store', default = os.getcwd(),
                   dest = 'source_dir',
                   help = 'Directory to use for the package [ False ]')
    p.add_argument('vm_id', action = 'store', default = None,
                   help = 'The vmware vmx filename for the vm to test [ None ]')
    p.add_argument('username', action = 'store', type = str, default = None,
                   help = 'VM username [ ]')
    p.add_argument('password', action = 'store', type = str, default = None,
                   help = 'VM username password [ ]')
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
    debug_args = []
    if args.debug:
      debug_args.append('--debug')
    if args.tty:
      debug_args.extend([ '--tty', tty ])
    cmd = [
      'bin/best.py',
      'vmware', 'vm_run_package',
    ] + debug_args + [
      args.vm_id,
      args.username,
      args.password,
      tmp_dir,
      self._ENTRY_COMMAND_FILENAME,
    ] + args.entry_command_args
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
python ./bin/bes_test.py --dont-hack-env --root-dir . ${1+"$@"}
exit $?
'''
  
if __name__ == '__main__':
  vmware_tester.run()
