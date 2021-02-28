#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path

from bes.fs.file_util import file_util
from bes.fs.temp_file import temp_file
from bes.system.execute import execute
from bes.system.process_lister import process_lister
from bes.system.which import which

from .vmware_app_base import vmware_app_base

class vmware_app_macos(vmware_app_base):

  @classmethod
  #@abstractmethod
  def is_installed(clazz):
    'Return True if vmware is installed.'
    return path.exists('/Applications/VMware Fusion.app/Contents/Public/vmrun')

  @classmethod
  #@abstractmethod
  def is_running(clazz):
    'Return True if vmware is installed.'
    vmware_command_name = '/Applications/VMware Fusion.app/Contents/MacOS/VMware Fusion'
    processes = process_lister().list_processes()
    for process in processes:
      if vmware_command_name in process.command:
        return True
    return False

  @classmethod
  #@abstractmethod
  def ensure_running(clazz):
    'Ensure vmware is running.'
    if clazz.is_running():
      return
    execute.execute('open -g /Applications/VMware\ Fusion.app')

  @classmethod
  #@abstractmethod
  def ensure_stopped(clazz):
    'Ensure vmware is stopped.'
    if not clazz.is_running():
      return
    tmp_applescript_content = '''\
tell application "VMWare Fusion"
    quit
end tell
'''
    tmp_applescript = temp_file.make_temp_file(content = tmp_applescript_content, suffix = '.scpt')
    cmd = [ 'osascript', tmp_applescript ]
    execute.execute(cmd)

  @classmethod
  #@abstractmethod
  def host_type(clazz):
    'Host type form vmrun authentication.'
    return 'fusion'

  @classmethod
  #@abstractmethod
  def preferences_filename(clazz):
    'The full path to the preferneces filename.'
    return path.expanduser('~/Library/Preferences/VMware Fusion/preferences')

  @classmethod
  #@abstractmethod
  def vmrun_exe_path(clazz):
    'The full path to the vmrun executable.'
    return which.which('vmrun')
  
