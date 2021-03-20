#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path
import pprint

from bes.cli.cli_command_handler import cli_command_handler
from bes.common.check import check

from .pip_error import pip_error
from .pip_project import pip_project
from .pip_installer_options import pip_installer_options

class pip_project_cli_handler(cli_command_handler):
  'pip project cli handler.'

  def __init__(self, cli_args):
    super(pip_project_cli_handler, self).__init__(cli_args, options_class = pip_installer_options)
    check.check_pip_installer_options(self.options)
    self.options.blurber.set_verbose(self.options.verbose)
    self._project = pip_project(self.options)

  def outdated(self):
    outdated = self._project.outdated()
    print(pprint.pformat(outdated))
    return 0

  def pip(self, args):
    check.check_string_seq(args)

    rv = self._project.pip(args)
    print(rv.stdout)
    return 0
  
