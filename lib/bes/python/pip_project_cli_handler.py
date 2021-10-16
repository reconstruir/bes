#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path
import pprint

from bes.cli.cli_command_handler import cli_command_handler
from bes.common.check import check
from bes.text.text_table import text_table
from bes.data_output.data_output import data_output

from .pip_error import pip_error
from .pip_project import pip_project
from .pip_project_options import pip_project_options

class pip_project_cli_handler(cli_command_handler):
  'pip project cli handler.'

  def __init__(self, cli_args):
    super(pip_project_cli_handler, self).__init__(cli_args, options_class = pip_project_options)
    check.check_pip_project_options(self.options)
    self.options.blurber.set_verbose(self.options.verbose)
    self._project = pip_project(self.options.name,
                                self.options.root_dir,
                                self.options.resolve_python_exe(),
                                debug = self.options.debug)
    
  def outdated(self):
    outdated = self._project.outdated()
    data_output.output_table(outdated, options = self.options.data_output_options)
    return 0

  def installed(self):
    installed = self._project.installed()
    data_output.output_table(installed, options = self.options.data_output_options)
    return 0
  
  def pip(self, args):
    check.check_string_seq(args)

    rv = self._project.pip(args)
    print(rv.stdout)
    return 0

  def install(self, package_name, version):
    check.check_string(package_name)
    check.check_string(version, allow_none = True)

    self._project.install(package_name, version = version)
    return 0

  def upgrade(self, package_name):
    check.check_string(package_name)

    self._project.upgrade(package_name)
    return 0

  def install_requirements(self, requirements_file):
    check.check_string(requirements_file)

    self._project.install_requirements(requirements_file)
    return 0

  def init(self):
    return 0
  
  def activate_script(self, variant):
    check.check_string(variant, allow_none = True)

    script = self._project.activate_script(variant = variant)
    print(script)
    return 0
  
