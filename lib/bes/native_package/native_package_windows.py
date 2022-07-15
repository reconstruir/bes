#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os
import os.path as path

from ..system.check import check

from .native_package_base import native_package_base
from .native_package_error import native_package_error
from .native_package_util import native_package_util

class native_package_windows(native_package_base):

  def __init__(self, blurber = None):
    super(native_package_windows, self).__init__(blurber)
  
  #@abstractmethod
  def installed_packages(self):
    'Return a list of installed pacakge.'
    return []

  #@abstractmethod
  def package_files(self, package_name):
    'Return a list of installed files for the given package.'
    return []

  #@abstractmethod
  def package_dirs(self, package_name):
    'Return a list of installed files for the given package.'
    return []

  #@abstractmethod
  def is_installed(self, package_name):
    'Return True if native_package is installed.'
    return False

  #@abstractmethod
  def owner(self, filename):
    'Return the package that owns filename.'
    return None
    
  #@abstractmethod
  def package_info(self, package_name):
    'Return platform specific information about a package.'
    return {}

  #@abstractmethod
  def remove(self, package_name, force_package_root):
    'Remove a package.'
    check.check_string(package_name)
    check.check_bool(force_package_root)

  #@abstractmethod
  def install(self, package_filename):
    'Install a package.'
    check.check_string(package_filename)
