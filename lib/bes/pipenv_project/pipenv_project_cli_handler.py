#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path
import pprint

from bes.cli.cli_command_handler import cli_command_handler
from bes.common.check import check
from bes.text.text_table import text_table
from bes.data_output.data_output import data_output

from .pipenv_project import pipenv_project
from .pipenv_project_options import pipenv_project_options

class pipenv_project_cli_handler(cli_command_handler):
  'pip project cli handler.'

  def __init__(self, cli_args):
    super(pipenv_project_cli_handler, self).__init__(cli_args, options_class = pipenv_project_options)
    check.check_pipenv_project_options(self.options)
    self.options.blurber.set_verbose(self.options.verbose)

  def create(self):
    project = pipenv_project(name, options = self.options)
    return 0

  def command(self, args):
    check.check_string_seq(args)

    project = pipenv_project(name, options = self.options)
    rv = project.call_pipenv(args)
    print(rv.stdout)
    return rv.exit_code

  def install(self, packages, dev):
    check.check_string_seq(packages)
    check.check_bool(dev)

    project = pipenv_project(name, options = self.options)
    rv = project.install(packages, dev = dev)
    print(rv.stdout)
    return 0

  def graph(self):
    project = pipenv_project(name, options = self.options)
    tree = project.graph()
    print(tree)
    return 0
