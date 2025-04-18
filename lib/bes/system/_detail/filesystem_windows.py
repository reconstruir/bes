#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-
from __future__ import print_function

import ctypes
import os
import os.path as path
import stat
import subprocess
from ctypes import wintypes

from .filesystem_base import filesystem_base

GetCurrentProcess = ctypes.windll.kernel32.GetCurrentProcess
GetCurrentProcess.restype = wintypes.HANDLE
OpenProcessToken = ctypes.windll.advapi32.OpenProcessToken
OpenProcessToken.argtypes = (wintypes.HANDLE, wintypes.DWORD, ctypes.POINTER(wintypes.HANDLE))
OpenProcessToken.restype = wintypes.BOOL

class LUID(ctypes.Structure):
  _fields_ = [
    ('low_part', wintypes.DWORD),
    ('high_part', wintypes.LONG),
    ]

  def __eq__(self, other):
    return (
      self.high_part == other.high_part and
      self.low_part == other.low_part
      )

  def __ne__(self, other):
    return not (self==other)

LookupPrivilegeValue = ctypes.windll.advapi32.LookupPrivilegeValueW
LookupPrivilegeValue.argtypes = (
  wintypes.LPWSTR, # system name
  wintypes.LPWSTR, # name
  ctypes.POINTER(LUID),
  )
LookupPrivilegeValue.restype = wintypes.BOOL

class TOKEN_INFORMATION_CLASS:
  TokenUser = 1
  TokenGroups = 2
  TokenPrivileges = 3
  # ... see http://msdn.microsoft.com/en-us/library/aa379626%28VS.85%29.aspx

SE_PRIVILEGE_ENABLED_BY_DEFAULT = (0x00000001)
SE_PRIVILEGE_ENABLED            = (0x00000002)
SE_PRIVILEGE_REMOVED            = (0x00000004)
SE_PRIVILEGE_USED_FOR_ACCESS    = (0x80000000)

class LUID_AND_ATTRIBUTES(ctypes.Structure):
  _fields_ = [
    ('LUID', LUID),
    ('attributes', wintypes.DWORD),
    ]

  def is_enabled(self):
    return bool(self.attributes & SE_PRIVILEGE_ENABLED)

  def enable(self):
    self.attributes |= SE_PRIVILEGE_ENABLED

  def get_name(self):
    size = wintypes.DWORD(10240)
    buf = ctypes.create_unicode_buffer(size.value)
    res = LookupPrivilegeName(None, self.LUID, buf, size)
    if res == 0: raise RuntimeError
    return buf[:size.value]

  def __str__(self):
    res = self.get_name()
    if self.is_enabled(): res += ' (enabled)'
    return res

LookupPrivilegeName = ctypes.windll.advapi32.LookupPrivilegeNameW
LookupPrivilegeName.argtypes = (
  wintypes.LPWSTR, # lpSystemName
  ctypes.POINTER(LUID), # lpLuid
  wintypes.LPWSTR, # lpName
  ctypes.POINTER(wintypes.DWORD), #cchName
  )
LookupPrivilegeName.restype = wintypes.BOOL

class TOKEN_PRIVILEGES(ctypes.Structure):
  _fields_ = [
    ('count', wintypes.DWORD),
    ('privileges', LUID_AND_ATTRIBUTES*0),
    ]

  def get_array(self):
    array_type = LUID_AND_ATTRIBUTES*self.count
    privileges = ctypes.cast(self.privileges, ctypes.POINTER(array_type)).contents
    return privileges

  def __iter__(self):
    return iter(self.get_array())

PTOKEN_PRIVILEGES = ctypes.POINTER(TOKEN_PRIVILEGES)

GetTokenInformation = ctypes.windll.advapi32.GetTokenInformation
GetTokenInformation.argtypes = [
  wintypes.HANDLE, # TokenHandle
  ctypes.c_uint, # TOKEN_INFORMATION_CLASS value
  ctypes.c_void_p, # TokenInformation
  wintypes.DWORD, # TokenInformationLength
  ctypes.POINTER(wintypes.DWORD), # ReturnLength
  ]
GetTokenInformation.restype = wintypes.BOOL

# http://msdn.microsoft.com/en-us/library/aa375202%28VS.85%29.aspx
AdjustTokenPrivileges = ctypes.windll.advapi32.AdjustTokenPrivileges
AdjustTokenPrivileges.restype = wintypes.BOOL
AdjustTokenPrivileges.argtypes = [
  wintypes.HANDLE,        # TokenHandle
  wintypes.BOOL,          # DisableAllPrivileges
  PTOKEN_PRIVILEGES,        # NewState (optional)
  wintypes.DWORD,         # BufferLength of PreviousState
  PTOKEN_PRIVILEGES,        # PreviousState (out, optional)
  ctypes.POINTER(wintypes.DWORD), # ReturnLength
  ]

def get_process_token():
  """
  Get the current process token
  """
  token = wintypes.HANDLE()
  TOKEN_ALL_ACCESS = 0xf01ff
  res = OpenProcessToken(GetCurrentProcess(), TOKEN_ALL_ACCESS, token)
  if not res > 0: raise RuntimeError("Couldn't get process token")
  return token

def get_symlink_luid():
  """
  Get the LUID for the SeCreateSymbolicLinkPrivilege
  """
  symlink_luid = LUID()
  res = LookupPrivilegeValue(None, "SeCreateSymbolicLinkPrivilege", symlink_luid)
  if not res > 0: raise RuntimeError("Couldn't lookup privilege value")
  return symlink_luid

def get_privilege_information():
  """
  Get all privileges associated with the current process.
  """
  # first call with zero length to determine what size buffer we need

  return_length = wintypes.DWORD()
  params = [
    get_process_token(),
    TOKEN_INFORMATION_CLASS.TokenPrivileges,
    None,
    0,
    return_length,
    ]

  res = GetTokenInformation(*params)

  # assume we now have the necessary length in return_length

  buffer = ctypes.create_string_buffer(return_length.value)
  params[2] = buffer
  params[3] = return_length.value

  res = GetTokenInformation(*params)
  assert res > 0, "Error in second GetTokenInformation (%d)" % res

  privileges = ctypes.cast(buffer, ctypes.POINTER(TOKEN_PRIVILEGES)).contents
  return privileges

def report_privilege_information():
  """
  Report all privilege information assigned to the current process.
  """
  privileges = get_privilege_information()
  print("found {0} privileges".format(privileges.count))
  tuple(map(print, privileges))

def enable_symlink_privilege():
  """
  Try to assign the symlink privilege to the current process token.
  Return True if the assignment is successful.
  """
  # create a space in memory for a TOKEN_PRIVILEGES structure
  #  with one element
  size = ctypes.sizeof(TOKEN_PRIVILEGES)
  size += ctypes.sizeof(LUID_AND_ATTRIBUTES)
  buffer = ctypes.create_string_buffer(size)
  tp = ctypes.cast(buffer, ctypes.POINTER(TOKEN_PRIVILEGES)).contents
  tp.count = 1
  tp.get_array()[0].enable()
  tp.get_array()[0].LUID = get_symlink_luid()
  token = get_process_token()
  res = AdjustTokenPrivileges(token, False, tp, 0, None, None)
  if res == 0:
    raise RuntimeError("Error in AdjustTokenPrivileges")

  ERROR_NOT_ALL_ASSIGNED = 1300
  return ctypes.windll.kernel32.GetLastError() != ERROR_NOT_ALL_ASSIGNED

class filesystem_windows(filesystem_base):

  @classmethod
  #@abstractmethod
  def free_disk_space(clazz, directory):
    'Return the free space for directory in bytes.'
    bytes_free = ctypes.c_ulonglong(0)
    native_directory = ctypes.c_wchar_p(directory)
    bytes_free_pointer = ctypes.pointer(bytes_free)
    ctypes.windll.kernel32.GetDiskFreeSpaceExW(native_directory, None, None, bytes_free_pointer)
    return bytes_free.value

  @classmethod
  #@abstractmethod
  def sync(clazz):
    'Sync the filesystem.'
    # FIXME: needs windows impl
    pass

  @classmethod
  #@abstractmethod
  def has_symlinks(clazz):
    'Return True if this system has support for symlinks.'
    # https://stackoverflow.com/questions/2094663/determine-if-windows-process-has-privilege-to-create-symbolic-link
    return enable_symlink_privilege()
  
  @classmethod
  #@abstractmethod
  def remove_directory(clazz, d):
    'Recursively remove a directory.'

    if 'SYSTEMROOT' in os.environ:
      system_root = os.environ['SYSTEMROOT']
    else:
      system_root = r'C:\Windows'
    cmd_exe = path.join(system_root, 'system32', 'cmd.exe')
    cmd = [
      cmd_exe, '/C', 'rmdir', '/S', '/Q', d,
    ]
    subprocess.check_call(cmd)

  @classmethod
  #@abstractmethod
  def max_filename_length(clazz):
    'Return the maximum allowed length for a filename.'
    return wintypes.MAX_PATH

  @classmethod
  #@abstractmethod
  def max_path_length(clazz):
    'Return the maximum allowed length for a path.'
    return wintypes.MAX_PATH

  @classmethod
  #@abstractmethod
  def file_is_hidden(clazz, filename):
    'Return True if filename is a hidden file.'
    normalized_filename = path.normpath(path.abspath(filename))
    basename = path.basename(normalized_filename)
    if basename.startswith('.'):
        return True
    return clazz._has_hidden_attribute(filename)

  @classmethod
  def _has_hidden_attribute(clazz, filename):
    st = os.stat(filename)
    if not hasattr(st, 'st_file_attributes'):
      return False
    return bool(st.st_file_attributes & stat.FILE_ATTRIBUTE_HIDDEN)

  @classmethod
  #@abstractmethod
  def filesystem_id(clazz, filename):
    'Return the id for the filesystem filename is found in.'
    statvfs = os.statvfs(filename)
    return statvfs.f_fsid
  
