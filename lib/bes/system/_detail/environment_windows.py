#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os
import os.path as path

from .environment_base import environment_base

class environment_windows(environment_base):

  @classmethod
  #@abstractmethod
  def home_dir(clazz):
    'Return the current users home dir.'

    home_drive = os.environ.get('HOMEDRIVE')
    home_path = os.environ.get('HOMEPATH')
    return home_drive + home_path

  @classmethod
  #@abstractmethod
  def username(clazz):
    'Return the current users username.'
    return os.environ.get('USERNAME')
  
  @classmethod
  #@abstractmethod
  def home_dir_env(clazz, home_dir):
    'Return a dict with the environment needed to set the home directory.'

    homedrive, homepath = path.splitdrive(home_dir)
    return {
      'HOME': home_dir,
      'HOMEDRIVE': homedrive,
      'HOMEPATH': homepath,
      'APPDATA': path.join(home_dir, 'AppData\\Roaming')
    }

  @classmethod
  #@abstractmethod
  def default_path(clazz):
    'The default system PATH.'
    return [
      r'C:\WINDOWS\system32',
      r'C:\WINDOWS',
      r'C:\WINDOWS\System32\Wbem',
    ]
  
  @classmethod
  #@abstractmethod
  def clean_path(clazz):
    'A clean system PATH with only the bare minimum needed to run shell commands.'
    return clazz.default_path()

  @classmethod
  #@abstractmethod
  def clean_variables(clazz):
    'A list of variables clean system PATH with only the bare minimum needed to run shell commands.'
    return [
      'ALLUSERSPROFILE',
      'APPDATA',
      'COMPUTERNAME',
      'COMSPEC',
      'DRIVERDATA',
      'HOME',
      'HOMEDRIVE',
      'HOMEPATH',
      'LOCALAPPDATA',
      'LOGONSERVER',
      'NUMBER_OF_PROCESSORS',
      'OS',
      'PATH',
      'PATHEXT',
      'PROCESSOR_ARCHITECTURE',
      'PROCESSOR_IDENTIFIER',
      'PROCESSOR_LEVEL',
      'PROCESSOR_REVISION',
      'SESSIONNAME',
      'SYSTEMDRIVE',
      'SYSTEMROOT',
      'TEMP',
      'TMP',
      'TMPDIR',
      'USERNAME',
      'USERPROFILE',
      'WINDIR',
    ]
