#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path
import pprint

from bes.cli.cli_command_handler import cli_command_handler
from bes.common.check import check
from bes.text.text_table import text_table

from .pipenv_project_error import pipenv_project_error
from .pipenv_project import pipenv_project
from .pipenv_project_options import pipenv_project_options

class pipenv_project_cli_handler(cli_command_handler):
  'pip project cli handler.'

  def __init__(self, cli_args):
    super(pipenv_project_cli_handler, self).__init__(cli_args, options_class = pipenv_project_options)
    check.check_pipenv_project_options(self.options)
    self.options.blurber.set_verbose(self.options.verbose)
    self._project = pipenv_project(options = self.options)
    
  def outdated(self):
    outdated = self._project.outdated()
    print(pprint.pformat(outdated))
    return 0

  def installed(self):
    installed = self._project.installed()

    tt = text_table(data = installed)
#    tt.set_labels(installed[0]._fields)
    print(tt)
    
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
  
