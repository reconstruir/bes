#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from ..system.check import check
from bes.cli.cli_command_handler import cli_command_handler
from bes.system.command_line import command_line

from .git_repo_script_options import git_repo_script_options
from .git_util import git_util

class git_repo_script_cli_handler(cli_command_handler):

  def __init__(self, cli_args):
    super(git_repo_script_cli_handler, self).__init__(cli_args, options_class = git_repo_script_options)
    check.check_git_repo_script_options(self.options)
  
  def repo_run_scripts(self, address, scripts):
    check.check_string(address)

    v = [ self._parse_script(script) for script in scripts ]
    result = git_util.repo_run_scripts(address, v, options = self.options)
    if self.options.verbose:
      print('status:\n{}\n'.format(result.status))
      print('  diff:\n{}\n'.format(result.diff))
      for rv in result.results:
        print('{}'.format(rv.script))
        print('{}'.format(rv.stdout))
    return 0

  @classmethod
  def _parse_script(clazz, cmd):
    args = command_line.parse_args(cmd)
    return git_util.script(args[0], args[1:])
  
