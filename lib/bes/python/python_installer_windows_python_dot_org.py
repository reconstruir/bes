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

class python_installer_windows_python_dot_org(python_installer_base):
  'Python installer for windows from python.org'
  
  def __init__(self, blurber):
    super(python_installer_windows_python_dot_org, self).__init__(blurber)

  #@abstractmethod
  def available_versions(self, num):
    'Return a list of python versions available to install.'
    check.check_int(num)

    return python_python_dot_org.available_versions(num)
    
  #@abstractmethod
  def installed_versions(self):
    'Return a list of installed python versions.'
    assert False
    
  #@abstractmethod
  def install(self, full_version):
    'Install the major.minor.revision full version of python.'
    check.check_string(full_version)

    assert False
        
  #@abstractmethod
  def uninstall(self, version_or_full_version):
    'Uninstall a python by version or full_version.'
    check.check_string(version_or_full_version)

    assert False

  #@abstractmethod
  def download(self, full_version):
    'Download the major.minor.revision full version of python to a temporary file.'
    url = python_python_dot_org.windows_package_url(full_version)
    tmp_pkg = python_python_dot_org.downlod_package_to_temp_file(url)
    return tmp_pkg
