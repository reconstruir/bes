#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
import time

from bes.fs.file_find import file_find
from bes.fs.file_util import file_util
from bes.fs.temp_file import temp_file
from bes.property.cached_class_property import cached_class_property
from bes.system.execute import execute
from bes.system.process_lister import process_lister
from bes.system.which import which

from .bat_vmware_app_base import bat_vmware_app_base

class bat_vmware_app_macos(bat_vmware_app_base):

  _APP_PATH = '/Applications/VMware Fusion.app'

  @classmethod
  #@abstractmethod
  def install_path(clazz):
    'The full path to where vmware is installed.'
    return clazz._APP_PATH
  
  @classmethod
  #@abstractmethod
  def is_installed(clazz):
    'Return True if vmware is installed.'
    return path.exists(f'{clazz._APP_PATH}/Contents/Public/vmrun')

  @classmethod
  #@abstractmethod
  def is_running(clazz):
    'Return True if vmware is installed.'
    vmware_command_name = f'{clazz._APP_PATH}/Contents/MacOS/VMware Fusion'
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
    execute.execute(f'open -g "{clazz._APP_PATH}"')

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
    time.sleep(1.0)

  @classmethod
  #@abstractmethod
  def host_type(clazz):
    'Host type form vmrun authentication.'
    return 'fusion'

  @classmethod
  #@abstractmethod
  def preferences_filename(clazz):
    'The full path to the preferences filename.'
    return path.expanduser('~/Library/Preferences/VMware Fusion/preferences')

  @classmethod
  #@abstractmethod
  def inventory_filename(clazz):
    'The full path to the preferences filename.'
    return path.expanduser('~/Library/Application Support/VMware Fusion/vmInventory')
  
  @classmethod
  #@abstractmethod
  def vmrun_exe_path(clazz):
    'The full path to the vmrun executable.'
    return clazz._found_vmrun_exe_path

  @classmethod
  #@abstractmethod
  def vmrest_exe_path(clazz):
    'The full path to the vmrest executable.'
    return clazz._found_vmrest_exe_path

  @classmethod
  #@abstractmethod
  def ovftool_exe_path(clazz):
    'The full path to the ovftool executable.'
    return clazz._found_ovftool_exe_path
  
  @classmethod
  def _find_exe(clazz, root_dir, exe_name):
    files = file_find.find(root_dir, relative = False, match_patterns = exe_name)
    if not files:
      return None
    assert len(files) == 1
    return files[0]

  @cached_class_property
  def _found_vmrun_exe_path(clazz):
    return clazz._find_exe(clazz._APP_PATH, 'vmrun')

  @cached_class_property
  def _found_vmrest_exe_path(clazz):
    return clazz._find_exe(clazz._APP_PATH, 'vmrest')

  @cached_class_property
  def _found_ovftool_exe_path(clazz):
    return clazz._find_exe(clazz._APP_PATH, 'ovftool')
  
