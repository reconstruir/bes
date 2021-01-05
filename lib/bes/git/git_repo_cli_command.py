#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from bes.common.check import check
from bes.cli.argparser_handler import argparser_handler

from .git import git
from .git_output import git_output
from .git_repo_cli_options import git_repo_cli_options
from .git_util import git_util

class git_repo_cli_command(object):

  @classmethod
  def handle_command(clazz, command, **kargs):
    options = git_repo_cli_options(**kargs)
    filtered_args = argparser_handler.filter_keywords_args(git_repo_cli_options, kargs)
    func = getattr(git_repo_cli_command, command)
    return func(options, **filtered_args)
  
  @classmethod
  def bump_tag(clazz, options, component, reset_lower):
    check.check_git_clone_options(options)

    result = git_util.repo_bump_tag(options.address, component, options.dry_run, reset_lower)
    if options.dry_run:
      print('dry_run: old_tag={} new_tag={}'.format(result.old_tag, result.new_tag))
    return 0

  @classmethod
  def greatest_tag(clazz, options):
    check.check_git_clone_options(options)
    
    greatest_tag = git_util.repo_greatest_tag(options.address)
    git_output.output_string(greatest_tag, options)
    return 0

  @classmethod
  def clone(clazz, options, dest_dir):
    check.check_git_clone_options(options)
    check.check_string(dest_dir)
    git.clone(options.address, dest_dir, options = options) 
    return 0
  
  @classmethod
  def sync(clazz, options, dest_dir):
    check.check_git_clone_options(options)
    check.check_string(dest_dir)

    git.sync(options.address, dest_dir, options = options) 
    return 0
