#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import codecs
from os import path
import subprocess

from bes.common.check import check
from bes.fs.temp_file import temp_file
from bes.fs.file_util import file_util
from bes.python.python_exe import python_exe
from bes.python.python_version import python_version
from bes.python.python_version_list import python_version_list
from bes.system.execute import execute
from bes.system.log import logger
from bes.url.url_util import url_util

from .python_installer_base import python_installer_base
from .python_installer_error import python_installer_error
from .python_installer_options import python_installer_options
from .python_python_dot_org import python_python_dot_org

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
    result = python_version_list()
    exes = python_exe.find_all_exes_info()
    for exe, info in exes.items():
      if info.source == 'python.org':
        full_version = python_exe.full_version(exe)
        result.append(full_version)
    result.sort()
    return result
    
  #@abstractmethod
  def install(self, version):
    '''
    Install any python version using any of these forms:
    major.minor.revision
    major.minor
    major
    The python.org windows installer exe is documented here:
    https://docs.python.org/3/using/windows.html
    '''
    version = python_version.check_version_any(version)
    
    self._log.log_method_d()
    available_versions = self.available_versions(0)
    self._log.log_d('install: available_versions: {}'.format(available_versions.to_string()))
    installed_versions = self.installed_versions()
    self._log.log_d('install: installed_versions: {}'.format(installed_versions.to_string()))

    matching_versions = available_versions.filter_by_version(version)
    matching_versions.sort()
    self._log.log_d('install: matching_versions: {}'.format(matching_versions.to_string()))

    if not matching_versions:
      raise python_installer_error('No python versions available for: {}'.format(version))
    
    if version.is_full_version():
      assert version == matching_versions[0]
      full_version = version
    else:
      full_version = matching_versions[-1]

    self._log.log_d('install: full_version: {}'.format(full_version))

    if full_version in installed_versions:
      raise python_installer_error('Already installed: {}'.format(full_version))
    
    if self.options.dry_run:
      url = python_python_dot_org.package_url('windows', full_version)
      self.blurb('dry-run: would install {}'.format(url))
      return

    tmp_package = self.download(full_version)
    self._log.log_d('install: tmp_package={}'.format(tmp_package))
    self.install_package(tmp_package)
    return True

  #@abstractmethod
  def update(self, version):
    'Update to the latest major.minor version of python.'
    python_version.check_version(version)
    assert False
    
  #@abstractmethod
  def install_package(self, package_filename):
    'Install a python package directly.  Not always supported.'
    check.check_string(package_filename)

    self._log.log_method_d()

    log_dir = temp_file.make_temp_dir(prefix = 'python_install_',
                                      suffix = '.dir',
                                      delete = not self.options.debug)
    install_log = path.join(log_dir, 'install.log')
    self._log.log_d('install_package: log_dir={}'.format(log_dir))
    cmd = [
      package_filename,
      '/log',
      log_dir,
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
    if rv.exit_code != 0:
      print(file_util.read(install_log, codec = 'utf-8'))
    
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
  def uninstall(self, version):
    '''Uninstall a python by version or full_version.'
    Uninstall a python version using any of these forms:
    major.minor.revision
    major.minor
    '''
    version = python_version.check_version_any(version)

    installed_versions = self.installed_versions()
    self._log.log_d('uninstall: installed_versions: {}'.format(installed_versions.to_string()))

    matching_versions = installed_versions.filter_by_version(version)
    matching_versions.sort()
    self._log.log_d('uninstall: matching_versions: {}'.format(matching_versions.to_string()))

    if not matching_versions:
      raise python_installer_error('Not installed: {}'.format(version))

    if len(matching_versions) != 1:
      raise python_installer_error('Somehow multiple installed versions found for {}: {}'.format(versiom,
                                                                                                 matching_versions.to_string()))
    full_version = matching_versions[0]
    self._log.log_d('uninstall: full_version: {}'.format(full_version))
    assert full_version

    old_package = self.download(full_version)
    self._log.log_d('uninstall: old_package={}'.format(old_package))
    cmd = [
      old_package,
      '/uninstall',
      '/log',
      r'C:\tmp\puninstall.log',
      '/quiet',
      '/silent',
    ]
    self._log.log_d('uninstall: command={}'.format(' '.join(cmd)))
    rv = execute.execute(cmd, stderr_to_stdout = True, raise_error = False)
    self._log.log_d('uninstall: exit_code={} output={}'.format(rv.exit_code, rv.stdout))

  #@abstractmethod
  def download(self, full_version):
    'Download the major.minor.revision full version of python to a temporary file.'
    return python_python_dot_org.download_package('windows',
                                                  full_version,
                                                  debug = self.options.debug)

  #@abstractmethod
  def supports_full_version(self):
    'Return True if this installer supports installing by full version.'
    return True
  
