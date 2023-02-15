#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path
import pprint

from ..cli.cli_command_handler import cli_command_handler
from ..data_output.data_output import data_output
from ..fs.file_check import file_check
from ..system.check import check
from ..text.text_table import text_table

from .pip_error import pip_error
from .pip_project import pip_project
from .pip_project_options import pip_project_options

class pip_project_cli_handler(cli_command_handler):
  'pip project cli handler.'

  def __init__(self, cli_args):
    super(pip_project_cli_handler, self).__init__(cli_args, options_class = pip_project_options)
    check.check_pip_project_options(self.options)
    self.options.blurber.set_verbose(self.options.verbose)
    
  def outdated(self):
    project = pip_project(options = self.options)
    outdated = project.outdated()
    data_output.output_table(outdated, options = self.options.data_output_options)
    return 0

  def installed(self):
    project = pip_project(options = self.options)
    installed = project.installed()
    data_output.output_table(installed, options = self.options.data_output_options)
    return 0
  
  def pip(self, args):
    check.check_string_seq(args)

    project = pip_project(options = self.options)
    rv = project.pip(args)
    print(rv.stdout)
    return 0

  def install(self, package_name, version):
    check.check_string(package_name)
    check.check_string(version, allow_none = True)

    project = pip_project(options = self.options)
    project.install(package_name, version = version)
    return 0

  def upgrade(self, packages):
    check.check_string_seq(packages)

    project = pip_project(options = self.options)
    project.upgrade(packages)
    return 0

  def install_requirements(self, requirements_files):
    requirements_files = file_check.check_file_seq(requirements_files)

    project = pip_project(options = self.options)
    project.install_requirements(requirements_files)
    return 0

  def create(self):
    project = pip_project(options = self.options)
    return 0
  
  def activate_script(self, variant):
    check.check_string(variant, allow_none = True)

    project = pip_project(options = self.options)
    script = project.activate_script(variant = variant)
    print(script)
    return 0
  
  def version(self, package_name):
    check.check_string(package_name)

    project = pip_project(options = self.options)
    version = project.version(package_name)
    print(version)
    return 0
