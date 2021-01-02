#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path
from bes.git.git_temp_repo import git_temp_repo
from bes.git.git_unit_test import git_temp_home_func

from bes.testing.program_unit_test import program_unit_test

class test_git_cli_args(program_unit_test):

  _program = program_unit_test.resolve_program(__file__, '..', '..', '..', '..', 'bin', 'best.py')
  
  @git_temp_home_func()
  def test_repo_greatest_tag(self):
    config = '''\
add commit1 commit1
  kiwi.txt: kiwi.txt
tag rel/1.0.0 tag1 @commit1
add commit2 commit2
  lemon.txt: lemon.txt
tag rel/1.0.1 tag2 @commit2
add commit3 commit3
  melon.txt: melon.txt
tag rel/1.0.2 tag3 @commit3
'''
    r = git_temp_repo(remote = True)
    r.apply_config_text(config)
    args = [
      'git_repo',
      'greatest_tag',
      r.root,
    ]
    rv = self.run_program(self._program, args)
    self.assertEqual(0, rv.exit_code)
    self.assertEqual( 'rel/1.0.2', rv.output.strip() )

  @git_temp_home_func()
  def test_repo_bump_tag(self):
    config = '''\
add commit1 commit1
  kiwi.txt: kiwi.txt
tag 1.0.0 tag1 @commit1
'''
    r = git_temp_repo(remote = True)
    r.apply_config_text(config)
    args = [
      'git_repo',
      'bump_tag',
      r.root,
    ]
    rv = self.run_program(self._program, args)
    self.assertEqual(0, rv.exit_code)
    args = [
      'git_repo',
      'greatest_tag',
      r.root,
    ]
    rv = self.run_program(self._program, args)
    self.assertEqual(0, rv.exit_code)
    self.assertEqual( '1.0.1', rv.output.strip() )

  @git_temp_home_func()
  def test_repo_bump_tag_component_major(self):
    config = '''\
add commit1 commit1
  kiwi.txt: kiwi.txt
tag 1.0.0 tag1 @commit1
'''
    r = git_temp_repo(remote = True)
    r.apply_config_text(config)
    args = [
      'git_repo',
      'bump_tag',
      '--component', 'major',
      r.root,
    ]
    rv = self.run_program(self._program, args)
    self.assertEqual(0, rv.exit_code)
    args = [
      'git_repo',
      'greatest_tag',
      r.root,
    ]
    rv = self.run_program(self._program, args)
    self.assertEqual(0, rv.exit_code)
    self.assertEqual( '2.0.0', rv.output.strip() )

  @git_temp_home_func()
  def test_repo_bump_tag_component_minor(self):
    config = '''\
add commit1 commit1
  kiwi.txt: kiwi.txt
tag 1.0.0 tag1 @commit1
'''
    r = git_temp_repo(remote = True)
    r.apply_config_text(config)
    args = [
      'git_repo',
      'bump_tag',
      '--component', 'minor',
      r.root,
    ]
    rv = self.run_program(self._program, args)
    self.assertEqual(0, rv.exit_code)
    args = [
      'git_repo',
      'greatest_tag',
      r.root,
    ]
    rv = self.run_program(self._program, args)
    self.assertEqual(0, rv.exit_code)
    self.assertEqual( '1.1.0', rv.output.strip() )
    
  @git_temp_home_func()
  def test_repo_bump_tag_component_revision(self):
    config = '''\
add commit1 commit1
  kiwi.txt: kiwi.txt
tag 1.0.0 tag1 @commit1
'''
    r = git_temp_repo(remote = True)
    r.apply_config_text(config)
    args = [
      'git_repo',
      'bump_tag',
      '--component', 'revision',
      r.root,
    ]
    rv = self.run_program(self._program, args)
    self.assertEqual(0, rv.exit_code)
    args = [
      'git_repo',
      'greatest_tag',
      r.root,
    ]
    rv = self.run_program(self._program, args)
    self.assertEqual(0, rv.exit_code)
    self.assertEqual( '1.0.1', rv.output.strip() )

  @git_temp_home_func()
  def test_repo_bump_tag_component_major_reset_lower(self):
    config = '''\
add commit1 commit1
  kiwi.txt: kiwi.txt
tag 1.0.1 tag1 @commit1
'''
    r = git_temp_repo(remote = True)
    r.apply_config_text(config)
    args = [
      'git_repo',
      'bump_tag',
      '--component', 'major',
      '--reset-lower',
      r.root,
    ]
    rv = self.run_program(self._program, args)
    self.assertEqual(0, rv.exit_code)
    args = [
      'git_repo',
      'greatest_tag',
      r.root,
    ]
    rv = self.run_program(self._program, args)
    self.assertEqual(0, rv.exit_code)
    self.assertEqual( '2.0.0', rv.output.strip() )
    
if __name__ == '__main__':
  program_unit_test.main()
