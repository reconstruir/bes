#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path
import pprint

from bes.cli.cli_command_handler import cli_command_handler
from bes.common.check import check
from bes.text.text_table import text_table

from .pip_error import pip_error
from .pip_project_v2 import pip_project_v2
from .pip_installer_options import pip_installer_options

class pip_project_cli_handler(cli_command_handler):
  'pip project cli handler.'

  def __init__(self, cli_args):
    super(pip_project_cli_handler, self).__init__(cli_args, options_class = pip_installer_options)
    check.check_pip_installer_options(self.options)
    self.options.blurber.set_verbose(self.options.verbose)
    self._project = pip_project_v2(self.options.name,
                                   self.options.root_dir,
                                   self.options.python_exe,
                                   debug = self.options.debug)

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
  
