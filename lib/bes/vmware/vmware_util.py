#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system.log import logger
from bes.system.execute import execute
from bes.system.host import host
from bes.system.process_lister import process_lister

class vmware_util(object):

  _log = logger('vmware_util')

  @classmethod
  def killall_vmrest(clazz):
    rv = execute.execute('killall vmrest', raise_error = False)
    if rv.exit_code == 0:
      clazz._log.log_i('killed some vmrest')

  _VMWARE_COMMAND_NAME_MAP = {
    host.MACOS: '/Applications/VMware Fusion.app/Contents/MacOS/VMware Fusion',
    host.LINUX: 'foo',
    host.WINDOWS: 'dunno',
  }
      
  @classmethod
  def is_running(clazz):
    'Return True of vmware workstation/fusion is running'
    vmware_command_name = clazz._VMWARE_COMMAND_NAME_MAP[host.SYSTEM]
    processes = process_lister().list_processes()
    for process in processes:
      if vmware_command_name in process.command:
        return True
    return False
