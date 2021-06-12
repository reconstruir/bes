#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
import re

from .platform_determiner_base import platform_determiner_base

class platform_determiner_macos(platform_determiner_base):
  'macos platform determiner.'

  def __init__(self, platform):
    self._platform = platform
  
  #@abstractmethod
  def system(self):
    'system.'
    return 'macos'

  #@abstractmethod
  def distro(self):
    'distro.'
    return ''
  
  _LICENSE_RTF = '/System/Library/CoreServices/Setup Assistant.app/Contents/Resources/en.lproj/OSXSoftwareLicense.rtf'
  #@abstractmethod
  def codename(self):
    'codename.'
    if not path.exists(self._LICENSE_RTF):
      return None
    with open(self._LICENSE_RTF, 'r') as f:
      line = self._find_matching_line(f.readlines())
      if not line:
        return None
      f = re.findall(r'.*SOFTWARE\s+LICENSE\s+AGREEMENT\s+FOR\smacOS\s+([\w\s]+)', line)
      if f and len(f) == 1:
        return f[0].lower().replace(' ', '_')
    return 'unknown'

  @classmethod
  def _find_matching_line(clazz, lines):
    for line in lines:
      if 'SOFTWARE LICENSE AGREEMENT FOR' in line:
        return line
    return None
  
  #@abstractmethod
  def family(self):
    'distro family.'
    return None

  #@abstractmethod
  def version(self):
    'distro version.'
    return '.'.join(self._platform.mac_ver()[0].split('.')[0])

  #@abstractmethod
  def version_major(self):
    'distro version major number.'
    return self._platform.mac_ver()[0].split('.')[0]

  #@abstractmethod
  def version_minor(self):
    'distro version minor number.'
    return self._platform.mac_ver()[0].split('.')[1]
  
  #@abstractmethod
  def arch(self):
    'arch.'
    return self._platform.machine()
