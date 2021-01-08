#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from bes.common.check import check
from bes.cli.cli_command_handler import cli_command_handler

from .git import git
from .git_output import git_output
from .git_repo_cli_options import git_repo_cli_options
from .git_util import git_util

class git_repo_cli_command(cli_command_handler):

  def __init__(self, cli_args):
    super(git_repo_cli_command, self).__init__(cli_args, options_class = git_repo_cli_options)
    check.check_git_repo_cli_options(self.options)
  
  def bump_tag(self, component, reset_lower):
    result = git_util.repo_bump_tag(self.options.address, component, self.options.dry_run, reset_lower)
    if self.options.dry_run:
      print('dry_run: old_tag={} new_tag={}'.format(result.old_tag, result.new_tag))
    return 0

  def greatest_tag(self):
    greatest_tag = git_util.repo_greatest_tag(self.options.address)
    git_output.output_string(greatest_tag, self.options)
    return 0

  def clone(self, dest_dir):
    check.check_string(dest_dir)
    git.clone(self.options.address, dest_dir, options = self.options) 
    return 0
  
  def sync(self, dest_dir):
    check.check_string(dest_dir)

    git.sync(self.options.address, dest_dir, options = self.options) 
    return 0
