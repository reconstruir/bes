#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from bes.common.check import check
from bes.cli.argparser_handler import argparser_handler

from .git import git
from .git_clone_options import git_clone_options
from .git_util import git_util

class git_repo_cli_command(object):

  @classmethod
  def handle_command(clazz, command, **kargs):
    options = git_clone_options(**kargs)
    filtered_args = argparser_handler.filter_keywords_args(git_clone_options, kargs)
    func = getattr(git_repo_cli_command, command)
    return func(options, **filtered_args)
  
  @classmethod
  def repo_bump_tag(clazz, options, address, component, dry_run, reset_lower):
    check.check_git_clone_options(options)
    check.check_string(address)

    result = git_util.repo_bump_tag(address, component, dry_run, reset_lower)
    if dry_run:
      print('dry_run: old_tag={} new_tag={}'.format(result.old_tag, result.new_tag))
    return 0

  @classmethod
  def repo_greatest_tag(clazz, options, address):
    check.check_git_clone_options(options)
    check.check_string(address)
    
    greatest_tag = git_util.repo_greatest_tag(address)
    print(greatest_tag)
    return 0

  @classmethod
  def repo_run_scripts(clazz, options, address, scripts, options):
    check.check_git_clone_options(options)
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
  def repo_clone(clazz, options, address, dest_dir):
    check.check_git_clone_options(options)
    check.check_string(address)

    git.clone(address, dest_dir, options = options) 
    return 0
  
  @classmethod
  def repo_sync(clazz, options, address, dest_dir):
    check.check_git_clone_options(options)
    check.check_string(address)

    git.sync(address, dest_dir, options = options) 
    return 0
