#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os
import os.path as path

from ..system.check import check
from bes.common.string_util import string_util
from bes.fs.file_mime import file_mime
from bes.fs.file_util import file_util
from bes.property.cached_property import cached_property
from bes.system.host_info import host_info

from .vmware_error import vmware_error
from .vmware_properties_file import vmware_properties_file
from .bat_vmware_system_info import bat_vmware_system_info

class bat_bat_vmware_vmx_file(vmware_properties_file):
  'Class do deal with vmware vmx files'

  def __init__(self, filename = None, backup = False):
    super().__init__(filename, backup = backup)
                      
  @cached_property
  def nickname(self):
    'Return the nickname for a the vmx file'
    i = self.filename.rfind(os.sep)
    if i < 0:
      return None
    vmx = self.filename[i + 1:]
    return string_util.remove_tail(vmx, '.vmx')

  _UNKNOWN_GUEST_OS_DETAILED_DATA="""bitness='64' distroName='Unknown' distroVersion='0.0' familyName='Linux' kernelVersion='0.0' prettyName='Unknown Linux'"""
  
  @cached_property
  def system_info(self):
    'Return guest system info in bes.system.host_info format'
    guest_os = self.get_value_with_default('guestOS', None) or self.get_value_with_default('guestos', None)
    guest_os_detailed_data = self.get_value_with_default('guestOS.detailed.data',
                                                         self._UNKNOWN_GUEST_OS_DETAILED_DATA)
    return bat_vmware_system_info.system_info(guest_os, guest_os_detailed_data)

  @cached_property
  def system(self):
    'Return guest system info in bes.system.host_info format'
    return self.system_info.system

  @cached_property
  def display_name(self):
    'Return the display name of the vm in the vmware gui'
    for key in ( 'displayName', 'displayname' ):
      if self.has_value(key):
        return self.get_value(key)
    raise vmware_error('No displayname found: {self.filename}')

  @cached_property
  def uuid(self):
    'Return the uuid for the vm'
    return self.get_value('uuid.bios')

  @cached_property
  def interpreter(self):
    'Return the full path for the default command line interpreter for this system'
    if self.system == 'linux':
      return '/bin/bash'
    elif self.system == 'macos':
      return '/bin/bash'
    elif self.system == 'windows':
      #return r'C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe'
      return r'C:\Windows\System32\cmd.exe'
    else:
      raise vmware_error('Unknown vmware system: "{}"'.format(system))

  @cached_property
  def can_run_programs_arguments(self):
    'Return a string of arguments to the interpreter to simply prove it works.'
    if self.interpreter.endswith('bash'):
      return r'-c "exit 0"'
    elif self.interpreter.endswith('cmd.exe'):
      return r'exit 0'
    else:
      raise vmware_error('Unknown vmware system: "{}"'.format(system))
    
  @classmethod
  def is_vmx_file(clazz, filename):
    'Return True if filename is a vmx file'
    if not path.exists(filename):
      return False
    if not path.isfile(filename):
      raise vmware_error('Directory found instead of file: "{}"'.format(filename))
    if not file_mime.is_text(filename):
      return False
    content = file_util.read(filename, codec = 'utf-8')
    if not '.encoding = ' in content:
      return False
    if not 'config.version = ' in content:
      return False
    return True

  @classmethod
  def check_vmx_file(clazz, filename):
    'Raise an exception if filename is not a vmware vmx file.'
    check.check_string(filename)

    if not clazz.is_vmx_file(filename):
      raise vmware_error('Not a vmware vmx file: "{}"'.format(filename))
    return filename
