#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import copy, os, pprint

from bes.cli.cli_command_handler import cli_command_handler
from bes.common.algorithm import algorithm
from ..system.check import check
from bes.files.bf_path import bf_path
from bes.system.log import logger

from .native_package_error import native_package_error
from .native_package import native_package
from .native_package_options import native_package_options

class native_package_cli_handler(cli_command_handler):
  'native_package cli commands.'

  _log = logger('native_package')

  def __init__(self, cli_args):
    super(native_package_cli_handler, self).__init__(cli_args,
                                                     options_class = native_package_options)
    check.check_native_package_options(self.options)
    self._native_package = native_package(self.options.blurber)
  
  def list(self):
    packages = self._native_package.installed_packages()
    for p in packages:
      print(p)
    return 0

  def installed(self, package_name):
    check.check_string(package_name)

    if self._native_package.is_installed(package_name):
      return 0
    return 1

  def info(self, package_name):
    check.check_string(package_name)

    info = self._native_package.package_info(package_name)
    print(pprint.pformat(info))
    return 0

  def files(self, package_name, levels):
    check.check_string(package_name)

    files = self._native_package.package_files(package_name)
    if levels:
      files = [ self._level_path(p, levels) for p in files ]
      files = algorithm.unique(files)
    for f in files:
      print(f)
    return 0

  def dirs(self, package_name, levels, root_dir):
    check.check_string(package_name)

    dirs = self._native_package.package_dirs(package_name)
    if levels:
      dirs = [ self._level_path(p, levels) for p in dirs ]
      dirs = algorithm.unique(dirs)
    if root_dir:
      ancestor = file_path.common_ancestor(dirs)
      if ancestor:
        print(ancestor)
    else:
      for f in dirs:
        print(f)
    return 0
  
  @classmethod
  def _level_path(clazz, p, levels):
    return os.sep.join(p.split(os.sep)[0 : levels])
  
  def owner(self, filename):
    check.check_string(filename)

    owner = self._native_package.owner(filename)
    if owner:
      print(owner)
      return 0
    return 1
  
  def remove(self, package_name, force_package_root):
    check.check_string(package_name)
    check.check_bool(force_package_root)

    native_package_options.remove(package_name, force_package_root)
    return 0

  def install(self, package_filename):
    check.check_string(package_filename)

    self._native_package.install(package_filename)
    return 0
  
