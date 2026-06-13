#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.bcli.bcli_command_handler import bcli_command_handler
from bes.system.check import check

from . import uv_exe as uv_exe_module
from . import uv_project
from . import uv_project_options

class uv_project_command_handler(bcli_command_handler):

  def name(self):
    return 'uv_project'

  def _make_project(self, options):
    return uv_project.uv_project(options=uv_project_options.uv_project_options(
      verbose=options.verbose,
      debug=options.debug,
      uv_exe=options.uv_exe,
      python=options.python,
      root_dir=options.root_dir,
    ))

  def _command_create(self, options):
    self._make_project(options).ensure_ready()
    return 0

  def _command_install(self, package_name, version, options):
    check.check_string(package_name)
    check.check_string(version, allow_none=True)

    project = self._make_project(options)
    project.ensure_ready()
    project.install(package_name, version=version)
    return 0

  def _command_upgrade(self, packages, options):
    check.check_string_seq(packages)

    project = self._make_project(options)
    project.ensure_ready()
    project.upgrade(packages)
    return 0

  def _command_install_requirements(self, requirements_files, options):
    check.check_string_seq(requirements_files)

    project = self._make_project(options)
    project.ensure_ready()
    project.install_requirements(requirements_files)
    return 0

  def _command_installed(self, options):
    project = self._make_project(options)
    for item in project.installed():
      print(f'{item.name}=={item.version}')
    return 0

  def _command_outdated(self, options):
    project = self._make_project(options)
    for item in project.outdated():
      print(f'{item.name}: {item.current_version} -> {item.latest_version}')
    return 0

  def _command_version(self, package_name, options):
    check.check_string(package_name)

    project = self._make_project(options)
    print(project.version(package_name))
    return 0

  def _command_exe_path(self, options):
    exe = uv_exe_module.uv_exe.find_or_none(options.uv_exe)
    if exe:
      print(exe)
    return 0
