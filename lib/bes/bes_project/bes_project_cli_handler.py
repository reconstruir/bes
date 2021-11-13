#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path
import pprint

from bes.cli.cli_command_handler import cli_command_handler
from bes.common.check import check
from bes.text.text_table import text_table
from bes.data_output.data_output import data_output

from .pip_error import pip_error
from .bes_project import bes_project
from .bes_project_options import bes_project_options

class bes_project_cli_handler(cli_command_handler):
  'pip project cli handler.'

  def __init__(self, cli_args):
    super(bes_project_cli_handler, self).__init__(cli_args, options_class = bes_project_options)
    check.check_bes_project_options(self.options)
    self.options.blurber.set_verbose(self.options.verbose)
    
  def outdated(self, name):
    check.check_string(name)

    project = bes_project(name, options = self.options)
    outdated = project.outdated()
    data_output.output_table(outdated, options = self.options.data_output_options)
    return 0

  def installed(self, name):
    check.check_string(name)

    project = bes_project(name, options = self.options)
    installed = project.installed()
    data_output.output_table(installed, options = self.options.data_output_options)
    return 0
  
  def pip(self, name, args):
    check.check_string(name)
    check.check_string_seq(args)

    project = bes_project(name, options = self.options)
    rv = project.pip(args)
    print(rv.stdout)
    return 0

  def install(self, name, package_name, version):
    check.check_string(name)
    check.check_string(package_name)
    check.check_string(version, allow_none = True)

    project = bes_project(name, options = self.options)
    project.install(package_name, version = version)
    return 0

  def upgrade(self, name, packages):
    check.check_string(name)
    check.check_string_seq(packages)

    project = bes_project(name, options = self.options)
    project.upgrade(packages)
    return 0

  def install_requirements(self, name, requirements_file):
    check.check_string(name)
    check.check_string(requirements_file)

    project = bes_project(name, options = self.options)
    project.install_requirements(requirements_file)
    return 0

  def create(self, name):
    check.check_string(name)

    project = bes_project(name, options = self.options)
    return 0
  
  def activate_script(self, name, variant):
    check.check_string(name)
    check.check_string(variant, allow_none = True)

    project = bes_project(name, options = self.options)
    script = project.activate_script(variant = variant)
    print(script)
    return 0
  
  def version(self, name, package_name):
    check.check_string(name)
    check.check_string(package_name)

    project = bes_project(name, options = self.options)
    version = project.version(package_name)
    print(version)
    return 0
