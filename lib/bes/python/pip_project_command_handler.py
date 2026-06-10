#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.bcli.bcli_command_handler import bcli_command_handler
from bes.data_output.data_output import data_output
from bes.files.bf_check import bf_check
from bes.system.check import check

from .pip_project import pip_project
from .pip_project_options import pip_project_options

class pip_project_command_handler(bcli_command_handler):

  def name(self):
    return 'pip_project'

  def _make_project(self, options):
    return pip_project(options=pip_project_options(
      verbose=options.verbose,
      debug=options.debug,
      root_dir=options.root_dir,
      python_version=options.python_version,
      python_exe=options.python_exe,
      output_filename=options.output_filename,
      output_style=options.output_style,
      limit_num_items=options.limit_num_items,
    ))

  def _command_create(self, options):
    self._make_project(options)
    return 0

  def _command_install(self, package_name, version, options):
    check.check_string(package_name)
    check.check_string(version, allow_none=True)

    project = self._make_project(options)
    project.install(package_name, version=version)
    return 0

  def _command_upgrade(self, packages, options):
    check.check_string_seq(packages)

    project = self._make_project(options)
    project.upgrade(packages)
    return 0

  def _command_install_requirements(self, requirements_files, options):
    requirements_files = bf_check.check_file_seq(requirements_files)

    project = self._make_project(options)
    project.install_requirements(requirements_files)
    return 0

  def _command_outdated(self, options):
    project = self._make_project(options)
    outdated = project.outdated()
    data_output.output_table(outdated, options=project.options.data_output_options)
    return 0

  def _command_installed(self, options):
    project = self._make_project(options)
    installed = project.installed()
    data_output.output_table(installed, options=project.options.data_output_options)
    return 0

  def _command_pip(self, args, options):
    check.check_string_seq(args)

    project = self._make_project(options)
    rv = project.pip(args)
    print(rv.stdout)
    return 0

  def _command_activate_script(self, variant, options):
    check.check_string(variant, allow_none=True)

    project = self._make_project(options)
    script = project.activate_script(variant=variant)
    print(script)
    return 0

  def _command_version(self, package_name, options):
    check.check_string(package_name)

    project = self._make_project(options)
    version = project.version(package_name)
    print(version)
    return 0
