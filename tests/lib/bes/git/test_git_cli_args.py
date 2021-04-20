#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path
from bes.git.git_temp_repo import git_temp_repo
from bes.git.git_unit_test import git_temp_home_func

from bes.testing.program_unit_test import program_unit_test

class test_git_cli_args(program_unit_test):

  _program = program_unit_test.resolve_program(__file__, '..', '..', '..', '..', 'bin', 'best.py')

  @git_temp_home_func()
  def test_tag(self):
    config = '''\
add commit1 commit1
  kiwi.txt: kiwi.txt
tag 1.0.0 tag1 @commit1
'''
    r = git_temp_repo(remote = True, config = config)
    self.assertEqual( '1.0.0', r.greatest_local_tag().name )
    args = [
      'git',
      'tag',
      '--root-dir', r.root,
    ]
    rv = self.run_program(self._program, args)
    self.assertEqual(0, rv.exit_code)
    self.assert_string_equal_strip( '''\
local: 1.0.0
remote: 1.0.0
''', rv.output, native_line_breaks = True )
  
  @git_temp_home_func()
  def test_bump_tag_revision(self):
    'Just a smoke test bes.git has more test cases for bump_tag'
    content = [
      'file foo.txt "this is foo.txt" 644',
      'file bar.txt "this is bar.txt" 644',
    ]
    r1 = git_temp_repo(content = content, debug = self.DEBUG)
    r2 = r1.make_temp_cloned_repo()
    self.assertEqual( None, r1.greatest_local_tag() )

    args = [
      'git',
      'bump_tag',
      '--root-dir', r1.root,
      '--component', 'revision',
      '--reset-lower',
    ]
    rv = self.run_program(self._program, args)
    self.assertEqual(0, rv.exit_code)
    r2.pull()
    self.assertEqual( '1.0.0', r2.greatest_local_tag().name )

    args = [
      'git',
      'bump_tag',
      '--root-dir', r1.root,
      '--component', 'revision',
      '--reset-lower',
    ]
    rv = self.run_program(self._program, args)
    self.assertEqual(0, rv.exit_code)
    r2.pull()
    self.assertEqual( '1.0.1', r2.greatest_local_tag().name )

  @git_temp_home_func()
  def test_bump_tag_major(self):
    'Just a smoke test bes.git has more test cases for bump_tag'
    content = [
      'file foo.txt "this is foo.txt" 644',
      'file bar.txt "this is bar.txt" 644',
    ]
    r1 = git_temp_repo(content = content, debug = self.DEBUG)
    r2 = r1.make_temp_cloned_repo()
    self.assertEqual( None, r1.greatest_local_tag() )

    args = [
      'git',
      'bump_tag',
      '--root-dir', r1.root,
      '--component', 'revision',
      '--reset-lower',
    ]
    rv = self.run_program(self._program, args)
    self.assertEqual(0, rv.exit_code)
    r2.pull()
    self.assertEqual( '1.0.0', r2.greatest_local_tag().name )

    args = [
      'git',
      'bump_tag',
      '--root-dir', r1.root,
      '--component', 'major',
      '--reset-lower',
    ]
    rv = self.run_program(self._program, args)
    self.assertEqual(0, rv.exit_code)
    r2.pull()
    self.assertEqual( '2.0.0', r2.greatest_local_tag().name )

  @git_temp_home_func()
  def test_tags(self):
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
    r = git_temp_repo(remote = True, config = config)
    tmp_output_file = self.make_temp_file(suffix = '.txt')
    args = [
      'git',
      'tags',
      '--root-dir', r.root,
      '--output', tmp_output_file,
      '--style', 'brief',
    ]
    rv = self.run_program(self._program, args)
    self.assertEqual(0, rv.exit_code)
    self.assert_text_file_equal( '''\
rel/1.0.0
rel/1.0.1
rel/1.0.2
''', tmp_output_file, native_line_breaks = True )

  @git_temp_home_func()
  def test_bump_tag_with_prefix(self):
    config = '''\
add commit1 commit1
  kiwi.txt: kiwi.txt
tag rel/v2/1.0.0 tag1 @commit1
add commit2 commit2
  lemon.txt: lemon.txt
tag rel/v2/1.0.1 tag2 @commit2
add commit3 commit3
  melon.txt: melon.txt
tag rel/v2/1.0.2 tag3 @commit3
add commit4 commit4
  potato.txt: potato.txt
tag test/v3/1.0.0 tag4 @commit4
tag test/v3/1.0.1 tag5 @commit4
'''
    r = git_temp_repo(remote = True, config = config)
    args = [
      'git',
      'bump_tag',
      '--root-dir', r.root,
      '--component', 'revision',
      '--prefix', 'rel/v2/',
    ]
    self.assertEqual( 'rel/v2/1.0.2', r.greatest_local_tag(prefix = 'rel/v2/').name )
    self.assertEqual( 'test/v3/1.0.1', r.greatest_local_tag(prefix = 'test/v3/').name )

    rv = self.run_program(self._program, args)
    self.assertEqual(0, rv.exit_code)

    self.assertEqual( 'rel/v2/1.0.3', r.greatest_local_tag(prefix = 'rel/v2/').name )
    self.assertEqual( 'test/v3/1.0.1', r.greatest_local_tag(prefix = 'test/v3/').name )
    
if __name__ == '__main__':
  program_unit_test.main()
