#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path
from bes.testing.unit_test import unit_test

from bes.git.git_repo_cli_options import git_repo_cli_options
from bes.data_output.data_output_style import data_output_style

class test_git_repo_cli_options(unit_test):

  def test_no_args(self):
    o = git_repo_cli_options()
    self.assertEqual( {
      'address': None,
      'branch': None,
      'clean': False,
      'clean_immaculate': False,
      'debug': False,
      'depth': None,
      'dry_run': False,
      'enforce_empty_dir': True,
      'jobs': None,
      'lfs': False,
      'no_network': False,
      'num_tries': 1,
      'output_filename': None,
      'output_style': data_output_style.BRIEF,
      'reset_to_head': False,
      'retry_wait_seconds': 10.0,
      'shallow_submodules': False,
      'submodule_list': None,
      'submodules': False,
      'submodules_recursive': False,
      'verbose': False,
    }, o.__dict__)

  def test_address(self):
    o = git_repo_cli_options(address = 'foo')
    self.assertEqual( {
      'address': 'foo',
      'branch': None,
      'clean': False,
      'clean_immaculate': False,
      'debug': False,
      'depth': None,
      'dry_run': False,
      'enforce_empty_dir': True,
      'jobs': None,
      'lfs': False,
      'no_network': False,
      'num_tries': 1,
      'output_filename': None,
      'output_style': data_output_style.BRIEF,
      'reset_to_head': False,
      'retry_wait_seconds': 10.0,
      'shallow_submodules': False,
      'submodule_list': None,
      'submodules': False,
      'submodules_recursive': False,
      'verbose': False,
    }, o.__dict__)

  def test_common_part(self):
    o = git_repo_cli_options(dry_run = True,
                             output_filename = 'foo.out',
                             output_style = 'json')
    self.assertEqual( {
      'address': None,
      'branch': None,
      'clean': False,
      'clean_immaculate': False,
      'debug': False,
      'depth': None,
      'dry_run': True,
      'enforce_empty_dir': True,
      'jobs': None,
      'lfs': False,
      'no_network': False,
      'num_tries': 1,
      'output_filename': 'foo.out',
      'output_style': 'json',
      'reset_to_head': False,
      'retry_wait_seconds': 10.0,
      'shallow_submodules': False,
      'submodule_list': None,
      'submodules': False,
      'submodules_recursive': False,
      'verbose': False,
    }, o.__dict__)
    
if __name__ == '__main__':
  unit_test.main()
