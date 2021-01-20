#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path

from bes.system.execute import execute
from bes.system.process_lister import process_lister
from bes.fs.file_util import file_util
from bes.fs.temp_file import temp_file

from .vmware_app_base import vmware_app_base

class vmware_app_macos(vmware_app_base):

  #@abstractmethod
  def is_installed(self):
    'Return True if vmware is installed.'
    return path.exists('/Applications/VMware Fusion.app/Contents/Public/vmrun')

  #@abstractmethod
  def is_running(self):
    'Return True if vmware is installed.'
    vmware_command_name = '/Applications/VMware Fusion.app/Contents/MacOS/VMware Fusion'
    processes = process_lister().list_processes()
    for process in processes:
      if vmware_command_name in process.command:
        return True
    return False

  #@abstractmethod
  def ensure_running(self):
    'Ensure vmware is running.'
    if self.is_running():
      return
    execute.execute('open -g /Applications/VMware\ Fusion.app')

  #@abstractmethod
  def ensure_stopped(self):
    'Ensure vmware is stopped.'
    if not self.is_running():
      return
    tmp_applescript_content = '''\
tell application "VMWare Fusion"
    quit
end tell
'''
    tmp_applescript = temp_file.make_temp_file(content = tmp_applescript_content, suffix = '.scpt')
    cmd = [ 'osascript', tmp_applescript ]
    execute.execute(cmd)

  #@abstractmethod
  def host_type(self):
    'Host type form vmrun authentication.'
    return 'fusion'
