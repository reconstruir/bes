#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os, re
from os import path

from bes.common.check import check
from bes.fs.dir_util import dir_util
from bes.system.execute import execute
from bes.fs.file_symlink import file_symlink
from bes.fs.file_util import file_util

from bes.native_package.native_package import native_package
from bes.unix.sudo.sudo import sudo
from bes.unix.sudo.sudo_cli_options import sudo_cli_options

from .python_error import python_error
from .python_exe import python_exe
from .python_installer_base import python_installer_base
from .python_python_dot_org import python_python_dot_org
from .python_version import python_version

class python_installer_macos_python_dot_org(python_installer_base):
  'Python installer for macos from python.org'
  
  def __init__(self, blurber):
    super(python_installer_macos_python_dot_org, self).__init__(blurber)

  #@abstractmethod
  def available_versions(self, num):
    'Return a list of python versions available to install.'
    check.check_int(num)

    return python_python_dot_org.available_versions('macos', num)
    
  #@abstractmethod
  def installed_versions(self):
    'Return a list of installed python versions.'

    result = []
    np = native_package(self.options.blurber)
    all_packages = np.installed_packages()
    for package_name in all_packages:
      if 'PythonFramework' in package_name:
        exe = self._python_exe_for_package(np, package_name)
        if not exe:
          raise python_error('Failed to determine the python executable for possibly corrupted package: "{}"'.format(package_name))
        full_version = python_exe.full_version(exe)
        result.append(full_version)
    return sorted(result)
    
  #@abstractmethod
  def install(self, full_version):
    'Install the major.minor.revision full version of python.'
    check.check_string(full_version)

    version = python_version.version(full_version)
    installed_versions = self.installed_versions()
    
    if full_version in installed_versions:
      self.blurb('already installed: {}'.format(full_version))
      return False

    versions_to_uninstall = []
    for next_installed_full_version in installed_versions:
      next_installed_version = python_version.version(next_installed_full_version)
      if next_installed_version == version:
        versions_to_uninstall.append(next_installed_full_version)
    if versions_to_uninstall:
      self.blurb_verbose('need to uninstall: {}'.format(' '.join(versions_to_uninstall)))
    self._sudo_validate('sudo password for install:')

    url = python_python_dot_org.macos_package_url(full_version)
    tmp_pkg = python_python_dot_org.downlod_package_to_temp_file(url)
    
    for old_full_version in versions_to_uninstall:
      self.blurb('Uninstalling python {}'.format(old_full_version))
      self.uninstall(old_full_version)

    self.blurb('Installing python {}'.format(full_version))
    self.blurb_verbose('Installing: {}'.format(tmp_pkg))

    self.install_package(tmp_pkg)

    return True

  #@abstractmethod
  def install_package(self, package_filename):
    'Install a python package directly.  Not always supported.'
    check.check_string(package_filename)

    np = native_package(self.blurber)
    np.install(package_filename)

    self._run_commands(np, version)
    self._cleanup_links()
    #self._fix_symlinks(np, full_version)
    
  #@abstractmethod
  def uninstall(self, version_or_full_version):
    'Uninstall a python by version or full_version.'
    check.check_string(version_or_full_version)

    if python_version.is_version(version_or_full_version):
      result = self._uninstall_version(version_or_full_version)
    elif python_version.is_full_version(version_or_full_version):
      result = self._uninstall_full_version(version_or_full_version)
    else:
      raise python_error('Invalid python version: "{}"'.format(version_or_full_version))
    return result

  #@abstractmethod
  def download(self, full_version):
    'Download the major.minor.revision full version of python to a temporary file.'
    return python_python_dot_org.download_package('macos', full_version, debug = debug)
  
  def _uninstall_version(self, version):
    'Install the major.minor full version of python.'
    check.check_string(version)
    assert python_version.is_version(version)

    np = native_package(self.blurber)

    to_delete_package_names = self._python_package_names_for_version(version)
    if np.has_any_package(to_delete_package_names):
      self._sudo_validate('sudo password for uninstall:')

    result = False
    for package_name in to_delete_package_names:
      if np.has_package(package_name):
        result = True
        self.blurb_verbose('uninstalling {} - {}'.format(version, package_name))
        np.remove(package_name, False)

    garbage = [
      '/Applications/Python {}'.format(version),
      '/Library/Frameworks/Python.framework/Versions/{}'.format(version),
    ]

    for next_garbage in garbage:
      if path.exists(next_garbage):
        rv = True
        self._sudo_validate('sudo password for uninstall:')
        args = [ 'rm', '-rf', next_garbage ]
        sudo.call_sudo(args)
    return result

  def _uninstall_full_version(self, full_version):
    'Install the major.minor.revision full version of python.'
    check.check_string(full_version)
    assert python_version.is_full_version(full_version)

    version = python_version.version(full_version)
    np = native_package(self.blurber)
    package_name = 'org.python.Python.PythonFramework-{}'.format(version)
    if np.has_package(package_name):
      exe = self._python_exe_for_package(np, package_name)
      if not exe:
        raise python_error('Failed to determine the python executable for possibly corrupted package: "{}"'.format(package_name))
      actual_full_version = python_exe.full_version(exe)
      if actual_full_version != full_version:
        raise python_error('Python version mismatch.  expected={} actual={}'.format(full_version, actual_full_version))

    return self._uninstall_version(version)

  def _cleanup_links(self):
    self._cleanup_usr_local_links()
    self._cleanup_framework_links()
  
  @classmethod
  def _python_package_names_for_version(clazz, version):
    'Return a list of all the packages that get installed for a version of python.'
    check.check_string(version)
    assert python_version.is_version(version)
    
    return [
      'org.python.Python.PythonApplications-{}'.format(version),
      'org.python.Python.PythonDocumentation-{}'.format(version),
      'org.python.Python.PythonFramework-{}'.format(version),
      'org.python.Python.PythonUnixTools-{}'.format(version),
    ]
      
  @classmethod
  def _python_exe_for_package(clazz, np, package_name):
    'Return the python exe for a org.python.Python.PythonFramework-* package.'

    files = np.package_files(package_name)
    exe =  clazz._python_exe_from_package_files(files)
    if not path.isfile(exe):
      return None
    return exe

  @classmethod
  def _python_exe_from_package_files(clazz, files):
    'Return the python exe from a list of org.python.Python.PythonFramework-* package files.'
    for filename in files:
      if re.match(r'^.*/bin/python\d\.\d*$', filename):
        return filename
    return None

  @classmethod
  def _python_commands_for_package(clazz, np, package_name):
    'Return the *.command files for a org.python.Python.PythonFramework-* package.'

    files = np.package_files(package_name)
    return clazz._python_commands_for_package_files(files)
  
  @classmethod
  def _python_commands_for_package_files(clazz, files):
    'Return the *.command files for a org.python.Python.PythonApplications-* package'

    result = []
    for filename in files:
      if re.match(r'^.*\.command$', filename):
        result.append(filename)
    return result

  @classmethod
  def _sudo_validate(clazz, prompt):
    options = sudo_cli_options()
    options.prompt = prompt
    sudo.authenticate(options = options)

  def _run_commands(self, np, version):
    package_name = 'org.python.Python.PythonApplications-{}'.format(version)
    commands = self._python_commands_for_package(np, package_name)
    for command in commands:
      if path.isfile(command):
        self.blurb_verbose('Running command: {}'.format(command))
        rv = execute.execute([ command ])
      else:
        self.blurb('WARNING: Command not found: {}'.format(command))

  def _fix_symlinks(self, np, full_version):
    version = python_version.version(full_version)
    installed_versions = self.installed_versions()

  _FRAMEWORK_LINK_ROOT_DIR = '/Library/Frameworks/Python.framework'
  _FRAMEWORK_LINK_VERSIONS_ROOT_DIR = path.join(_FRAMEWORK_LINK_ROOT_DIR, 'Versions')
  _FRAMEWORK_LINK_CURRENT_ROOT_DIR = path.join(_FRAMEWORK_LINK_VERSIONS_ROOT_DIR, 'Current')
    
  def _create_framework_symlinks(self, version):
    assert python_version.is_version(version)

    version_root_dir = path.join(self._FRAMEWORK_LINK_VERSIONS_ROOT_DIR, version)

    if not path.exists(version_root_dir):
      raise python_error('Trying to create framework symlinks for missing python version: {}'.format(version_root_dir))

    file_symlink.symlink(version, self._FRAMEWORK_LINK_CURRENT_ROOT_DIR)
    file_symlink.symlink('Versions/Current/Headers', path.join(self._FRAMEWORK_LINK_ROOT_DIR, 'Headers'))
    file_symlink.symlink('Versions/Current/Python', path.join(self._FRAMEWORK_LINK_ROOT_DIR, 'Python'))
    file_symlink.symlink('Versions/Current/Resources', path.join(self._FRAMEWORK_LINK_ROOT_DIR, 'Resources'))

  def _cleanup_framework_links(self):
    self._remove_broken_symlink(self._FRAMEWORK_LINK_CURRENT_ROOT_DIR)
    self._remove_broken_symlink(path.join(self._FRAMEWORK_LINK_ROOT_DIR, 'Headers'))
    self._remove_broken_symlink(path.join(self._FRAMEWORK_LINK_ROOT_DIR, 'Python'))
    self._remove_broken_symlink(path.join(self._FRAMEWORK_LINK_ROOT_DIR, 'Resources'))

  def _remove_broken_symlink(self, link):
    if file_symlink.is_broken(link):
      self.blurb_verbose('Removing broken framework link: {}'.format(link))
      file_util.remove(link)

  def _cleanup_usr_local_links(self):
    'Cleanup symlinks in /usr/local/bin that break after uninstalling python'

    links = dir_util.list('/usr/local/bin')
    broken_links = [ l for l in links if file_symlink.is_broken(l) ]
    for broken_link in broken_links:
      target = os.readlink(broken_link)
      if 'Library/Frameworks/Python.framework/Versions' in target:
        self.blurb_verbose('Removing broken /usr/local link: {}'.format(broken_link))
        file_util.remove(broken_link)
