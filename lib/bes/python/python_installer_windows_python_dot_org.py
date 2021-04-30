#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import codecs
from os import path
import subprocess

from bes.common.check import check
from bes.url.url_util import url_util
from bes.system.execute import execute

from .python_exe import python_exe
from .python_error import python_error
from .python_installer_base import python_installer_base
from .python_python_dot_org import python_python_dot_org
from .python_version import python_version

class python_installer_windows_python_dot_org(python_installer_base):
  'Python installer for windows from python.org'
  
  def __init__(self, blurber):
    super(python_installer_windows_python_dot_org, self).__init__(blurber)

  #@abstractmethod
  def available_versions(self, num):
    'Return a list of python versions available to install.'
    check.check_int(num)

    return python_python_dot_org.available_versions('windows', num)
    
  #@abstractmethod
  def installed_versions(self):
    'Return a list of installed python versions.'
    result = []
    exes = python_exe.find_all_exes_info()
    for exe, info in exes.items():
      if info.source == 'python.org':
        full_version = python_exe.full_version(exe)
        result.append(full_version)
    return result
    
  #@abstractmethod
  def install(self, full_version):
    '''
    Install the major.minor.revision full version of python.
    The python.org windows installer exe is documented here:
    https://docs.python.org/3/using/windows.html
    '''
    check.check_string(full_version)

    version = python_version.version(full_version)
    installed_versions = self.installed_versions()
    available_versions = self.available_versions(0)
    
    if full_version in installed_versions:
      self.blurb('already installed: {}'.format(full_version))
      return False

    if not full_version in available_versions:
      self.blurb('version not available: "{}"'.format(full_version))
      return False

    tmp_package = self.download(full_version, debug = True)
    print('pack: {}'.format(tmp_package))

    cmd = [
      tmp_package,
      '/quiet',
      'InstallAllUsers=1',
      'PrependPath=0',
      'Shortcuts=0',
      'AssociateFiles=0',
      'Include_doc=0',
      'Include_launcher=0',
      'InstallLauncherAllUsers=0',
    ]
    rv = execute.execute(cmd)
    print('rv={}'.format(rv))

  #@abstractmethod
  def install_package(self, package_filename):
    'Install a python package directly.  Not always supported.'
    check.check_string(package_filename)

    print('package: {}'.format(package_filename))

    cmd = [
      package_filename,
      '/quiet',
      'InstallAllUsers=1',
      'PrependPath=0',
      'Shortcuts=0',
      'AssociateFiles=0',
      'Include_doc=0',
      'Include_launcher=0',
      'InstallLauncherAllUsers=0',
    ]
    rv = execute.execute(cmd)
    print('rv={}'.format(rv))
    
  #@abstractmethod
  def _is_installed_full_version(self, full_version):
    check.check_string(full_version)

    exes = python_exe.find_all_exes_info()
    for exe, info in exes.items():
      if info.source == 'python.org':
        next_full_version = python_exe.full_version(exe)
        if full_version == next_full_version:
          return full_version
    return None

  #@abstractmethod
  def _is_installed_version(self, version):
    check.check_string(version)

    exes = python_exe.find_all_exes_info()
    for exe, info in exes.items():
      if info.source == 'python.org':
        next_version = python_exe.version(exe)
        if version == next_version:
          return python_exe.full_version(exe)
    return None
    
  #@abstractmethod
  def uninstall(self, version_or_full_version):
    'Uninstall a python by version or full_version.'
    check.check_string(version_or_full_version)

    installed = self.installed_versions()
    full_version = None
    if python_version.is_full_version(version_or_full_version):
      if version_or_full_version not in installed:
        raise python_error('Not installed: {}'.format(version_or_full_version))
      full_version = version_or_full_version
    elif python_version.is_version(version_or_full_version):
      assert False, 'fixme'
    else: 
      raise python_error('Invalid version: "{}"'.format(version_or_full_version))

    assert full_version

    old_package = self.download(full_version)
    print('old_package={}'.format(old_package))

  #@abstractmethod
  def download(self, full_version, debug = False):
    'Download the major.minor.revision full version of python to a temporary file.'
    return python_python_dot_org.download_package('windows', full_version, debug = debug)
