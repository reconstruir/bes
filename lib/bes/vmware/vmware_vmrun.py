#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

#from collections import namedtuple
import os.path as path
#import multiprocessing
#import socket
#import sys
#import time
#import tempfile

from bes.system.log import logger
from bes.system.command_line import command_line
#from bes.system.host import host
from bes.common.check import check
#from bes.common.string_util import string_util
#from bes.fs.file_find import file_find
#from bes.fs.file_util import file_util
#from bes.fs.temp_file import temp_file
#from bes.archive.archiver import archiver
from bes.credentials.credentials import credentials

from .vmware_app import vmware_app
from .vmware_error import vmware_error
#from .vmware_local_vm import vmware_local_vm
#from .vmware_preferences import vmware_preferences
#from .vmware_session import vmware_session
#from .vmware_vm import vmware_vm
from .vmware_vmrun_exe import vmware_vmrun_exe
from .vmware_vmx_file import vmware_vmx_file

class vmware_vmrun(object):

  _log = logger('vmware_vmrun')
  
  def __init__(self, login_credentials = None):
    check.check_credentials(login_credentials, allow_none = True)

    self._login_credentials = login_credentials
    self._app = vmware_app()
    self._auth_args = self._make_vmrun_auth_args(self._app, self._login_credentials)

  def run(self, args, env = None, extra_env = None, cwd = None,
          non_blocking = False, shell = False, raise_error = False):
    parsed_args = command_line.parse_args(args)
    vmrun_exe_args = self._auth_args + parsed_args
    self._log.log_d('run: vm_run_program: vmrun_exe_args={}'.format(vmrun_exe_args))
    return vmware_vmrun_exe.call_vmrun(vmrun_exe_args,
                                       extra_env = extra_env,
                                       cwd = cwd,
                                       non_blocking = non_blocking,
                                       shell = shell,
                                       raise_error = raise_error)


  POWER_STATES = ( 'start', 'stop', 'reset', 'suspend', 'pause', 'unpause' )
  def power(self, vmx_filename, state, gui = False, hard = False):
    check.check_string(vmx_filename)
    check.check_string(state)
    check.check_bool(gui)
    check.check_bool(hard)

    vmware_vmx_file.check_vmx_file(vmx_filename)
    
    if state not in self.POWER_STATES:
      raise vmware_error('Invalid power state "{}"  Should be one of: {}'.format(state, ' '.join(self.POWER_STATES)))

    args = [ vmx_filename, state ]
    if state in ( 'start' ):
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
    return self.run(args)

  def file_copy_to(self, vmx_filename, local_filename, remote_filename):
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
    return self.run(args)

  def file_copy_from(self, vmx_filename, remote_filename, local_filename):
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
    return self.run(args)
  
  @classmethod
  def _make_vmrun_auth_args(clazz, app, cred):
    args = [ '-T', app.host_type() ]
    if cred:
      args.extend([ '-gu', cred.username ])
      args.extend([ '-gp', cred.password ])
    return args

