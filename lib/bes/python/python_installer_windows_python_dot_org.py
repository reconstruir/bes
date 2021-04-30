#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import codecs
from os import path
import subprocess

from bes.common.check import check
from bes.url.url_util import url_util
from bes.system.execute import execute
from bes.system.log import logger

from .python_exe import python_exe
from .python_error import python_error
from .python_installer_base import python_installer_base
from .python_python_dot_org import python_python_dot_org
from .python_version import python_version
from .python_installer_options import python_installer_options

class python_installer_windows_python_dot_org(python_installer_base):
  'Python installer for windows from python.org'

  _log = logger('python_installer')
  
  def __init__(self, options):
    check.check_python_installer_options(options)
    super(python_installer_windows_python_dot_org, self).__init__(options)

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
  def install(self, any_version):
    '''
    Install any python version using any of these forms:
    major.minor.revision
    major.minor
    major
    The python.org windows installer exe is documented here:
    https://docs.python.org/3/using/windows.html
    '''
    check.check_string(any_version)
    self._log.log_method_d()
    available_versions = self.available_versions(0)
    installed_versions = self.installed_versions()
    self._log.log_d('install: available_versions: {}'.format(' '.join(available_versions)))
    self._log.log_d('install: installed_versions: {}'.format(' '.join(installed_versions)))

    if python_version.is_full_version(any_version):
      full_version = any_version
    elif python_version.is_version(any_version):
      matching_versions = python_version.filter_by_version(available_versions, any_version)
      if not matching_versions:
        raise python_error('No versions available for: {}'.format(any_version))
      full_version = matching_versions[0]
    elif python_version.is_major_version(any_version):
      matching_versions = python_version.filter_by_major_version(available_versions, any_version)
      if not matching_versions:
        raise python_error('No versions available for: {}'.format(any_version))
      full_version = matching_versions[0]
    else:
      raise python_error('Invalid version: "{}"'.format(version_or_full_version))

    if self.options.dry_run:
      url = python_python_dot_org.package_url('windows', full_version)
      self.blurb('dry-run: would install {}'.format(url))
      return

    if full_version in installed_versions:
      self.blurb('already installed: {}'.format(full_version))
      return False

    version = python_version.version(full_version)
    matching_versions = python_version.filter_by_version(available_versions, any_version)
    self._log.log_d('install: version={} matching_versions={}'.format(version, matching_versions))
    
    tmp_package = self.download(full_version, debug = True)
    self._log.log_d('install: tmp_package={}'.format(tmp_package))
    self.install_package(tmp_package)

  #@abstractmethod
  def install_package(self, package_filename):
    'Install a python package directly.  Not always supported.'
    check.check_string(package_filename)

    self._log.log_method_d()

    cmd = [
      package_filename,
      '/log',
      r'C:\tmp\pinstall.log',
      '/quiet',
      '/silent',
      'InstallAllUsers=1',
      'PrependPath=0',
      'Shortcuts=0',
      'AssociateFiles=0',
      'Include_doc=0',
      'Include_launcher=0',
      'InstallLauncherAllUsers=0',
    ]
    self._log.log_d('install_package: command={}'.format(' '.join(cmd)))
    rv = execute.execute(cmd, stderr_to_stdout = True, raise_error = False)
    self._log.log_d('install_package: exit_code={} output={}'.format(rv.exit_code, rv.stdout))
    
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
      matching_versions = python_version.filter_by_version(installed, version_or_full_version)
      if not matching_versions:
        raise python_error('Not installed: {}'.format(version_or_full_version))
      if len(matching_versions) > 1:
        raise python_error('Multiple python versions found: {}'.format(' '.join(matching_versions)))
      full_version = matching_versions[0]
    else: 
      raise python_error('Invalid version: "{}"'.format(version_or_full_version))

    assert full_version

    old_package = self.download(full_version)
    print('old_package={}'.format(old_package))
    cmd = [
      old_package,
      '/uninstall',
      '/log',
      r'C:\tmp\puninstall.log',
#      '/passive',
      '/quiet',
      '/silent',
    ]
    self._log.log_d('uninstall: command={}'.format(' '.join(cmd)))
    rv = execute.execute(cmd, stderr_to_stdout = True, raise_error = False)
    self._log.log_d('uninstall: exit_code={} output={}'.format(rv.exit_code, rv.stdout))

  #@abstractmethod
  def download(self, full_version, debug = False):
    'Download the major.minor.revision full version of python to a temporary file.'
    return python_python_dot_org.download_package('windows', full_version, debug = debug)
