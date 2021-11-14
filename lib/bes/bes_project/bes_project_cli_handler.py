#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path
import pprint

from bes.cli.cli_command_handler import cli_command_handler
from bes.common.check import check
from bes.text.text_table import text_table
from bes.data_output.data_output import data_output

from .bes_project_error import bes_project_error
from .bes_project import bes_project
from .bes_project_options import bes_project_options

class bes_project_cli_handler(cli_command_handler):
  'bes_project project cli handler.'

  def __init__(self, cli_args):
    super(bes_project_cli_handler, self).__init__(cli_args, options_class = bes_project_options)
    check.check_bes_project_options(self.options)
    self.options.blurber.set_verbose(self.options.verbose)
    
  def activate_script(self, variant):
    check.check_string(variant, allow_none = True)

    project = bes_project(options = self.options)
    script = project.activate_script(variant = variant)
    print(script)
    return 0
  
  def ensure(self, python_versions):
    check.check_string_seq(python_versions)

    project = bes_project(options = self.options)
    project.ensure(python_versions)
    return 0
