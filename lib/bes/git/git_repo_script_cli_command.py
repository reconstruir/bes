#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from bes.common.check import check
from bes.cli.argparser_handler import argparser_handler
from bes.system.command_line import command_line

from .git_repo_script_options import git_repo_script_options
from .git_util import git_util

class git_repo_script_cli_command(object):

  @classmethod
  def handle_command(clazz, command, **kargs):
    options = git_repo_script_options(**kargs)
    filtered_args = argparser_handler.filter_keywords_args(git_repo_script_options, kargs)
    func = getattr(git_repo_script_cli_command, command)
    return func(options, **filtered_args)
  
  @classmethod
  def repo_run_scripts(clazz, options, address, scripts):
    check.check_git_repo_script_options(options)
    check.check_string(address)

    v = [ clazz._parse_script(script) for script in scripts ]
    result = git_util.repo_run_scripts(address, v, options = options)
    if options.verbose:
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
  
