#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os
import pprint

from bes.bcli.bcli_command_handler import bcli_command_handler
from bes.common.algorithm import algorithm
from bes.files.bf_path import bf_path
from bes.system.check import check

from .native_package import native_package
from .native_package_options import native_package_options

class native_package_command_handler(bcli_command_handler):

  def name(self):
    return 'native_package'

  def _make_native_package(self, options):
    opts = native_package_options(verbose=options.verbose,
                                  sudo_password=options.sudo_password)
    return native_package(opts.blurber)

  def _command_list(self, options):
    packages = self._make_native_package(options).installed_packages()
    for p in packages:
      print(p)
    return 0

  def _command_installed(self, package_name, options):
    check.check_string(package_name)

    if self._make_native_package(options).is_installed(package_name):
      return 0
    return 1

  def _command_info(self, package_name, options):
    check.check_string(package_name)

    info = self._make_native_package(options).package_info(package_name)
    print(pprint.pformat(info))
    return 0

  def _command_files(self, package_name, levels, options):
    check.check_string(package_name)

    files = self._make_native_package(options).package_files(package_name)
    if levels:
      files = [self._level_path(p, levels) for p in files]
      files = algorithm.unique(files)
    for f in files:
      print(f)
    return 0

  def _command_dirs(self, package_name, levels, root_dir, options):
    check.check_string(package_name)

    dirs = self._make_native_package(options).package_dirs(package_name)
    if levels:
      dirs = [self._level_path(p, levels) for p in dirs]
      dirs = algorithm.unique(dirs)
    if root_dir:
      ancestor = bf_path.common_ancestor(dirs)
      if ancestor:
        print(ancestor)
    else:
      for f in dirs:
        print(f)
    return 0

  @classmethod
  def _level_path(clazz, p, levels):
    return os.sep.join(p.split(os.sep)[0:levels])

  def _command_owner(self, filename, options):
    check.check_string(filename)

    owner = self._make_native_package(options).owner(filename)
    if owner:
      print(owner)
      return 0
    return 1

  def _command_remove(self, package_name, force_package_root, options):
    check.check_string(package_name)
    check.check_bool(force_package_root)

    native_package_options.remove(package_name, force_package_root)
    return 0

  def _command_install(self, package_filename, options):
    check.check_string(package_filename)

    self._make_native_package(options).install(package_filename)
    return 0
