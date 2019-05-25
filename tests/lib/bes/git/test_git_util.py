#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path
from bes.testing.unit_test import unit_test
from bes.git import git_util
from bes.git.git_temp_repo import git_temp_repo
from bes.git.git_unit_test import git_unit_test
from bes.system.env_override import env_override

class test_git_util(unit_test):
  
  def test_name_from_address(self):
    with env_override.temp_home() as env:
      git_unit_test.set_identity()
      self.assertEqual( 'bar', git_util.name_from_address('https://foohub.com/myproj/bar.git') )
      self.assertEqual( 'foo-bar-baz', git_util.name_from_address('git@git:foo-bar-baz.git') )
      r = git_temp_repo()
      self.assertEqual( path.basename(r.root), git_util.name_from_address(r.root) )

  def test_repo_greatest_tag(self):
    with env_override.temp_home() as env:
      git_unit_test.set_identity()
      r = git_temp_repo()
      r.add_file('readme.txt', 'readme is good')
      r.push('origin', 'master')
      r.tag('1.0.0')
      r.push_tag('1.0.0')
      self.assertEqual( '1.0.0', git_util.repo_greatest_tag(r.address) )
      r.tag('1.0.1')
      r.push_tag('1.0.1')
      self.assertEqual( '1.0.1', git_util.repo_greatest_tag(r.address) )
    
  def test_repo_bump_tag(self):
    with env_override.temp_home() as env:
      git_unit_test.set_identity()
      r1 = git_temp_repo()
      r2 = r1.make_temp_cloned_repo()
      r1.add_file('readme.txt', 'readme is good')
      r1.push('origin', 'master')

      rv = git_util.repo_bump_tag(r1.address, None, False)
      self.assertEqual( ( None, '1.0.0' ), rv )
      r2.pull()
      self.assertEqual( '1.0.0', r2.greatest_local_tag() )

      rv = git_util.repo_bump_tag(r1.address, None, False)
      self.assertEqual( ( '1.0.0', '1.0.1' ), rv )
      r2.pull()
      self.assertEqual( '1.0.1', r2.greatest_local_tag() )

      rv = git_util.repo_bump_tag(r1.address, None, False)
      self.assertEqual( ( '1.0.1', '1.0.2' ), rv )
      r2.pull()
      self.assertEqual( '1.0.2', r2.greatest_local_tag() )

  def test_repo_bump_tag_dry_run(self):
    with env_override.temp_home() as env:
      git_unit_test.set_identity()
      r1 = git_temp_repo()
      r2 = r1.make_temp_cloned_repo()
      r1.add_file('readme.txt', 'readme is good')
      r1.push('origin', 'master')

      rv = git_util.repo_bump_tag(r1.address, None, True)
      self.assertEqual( ( None, '1.0.0' ), rv )
      r2.pull()
      self.assertEqual( None, r2.greatest_local_tag() )

  def test_repo_bump_tag_single_number(self):
    with env_override.temp_home() as env:
      git_unit_test.set_identity()
      r1 = git_temp_repo()
      r2 = r1.make_temp_cloned_repo()
      r1.add_file('readme.txt', 'readme is good')
      r1.push('origin', 'master')
      r1.tag('666')
      r1.push_tag('666')

      git_util.repo_bump_tag(r1.address, None, False)
      r2.pull()
      self.assertEqual( '667', r2.greatest_local_tag() )

      git_util.repo_bump_tag(r1.address, None, False)
      r2.pull()
      self.assertEqual( '668', r2.greatest_local_tag() )

  def test_repo_run_script(self):
    with env_override.temp_home() as env:
      git_unit_test.set_identity()
      r = git_temp_repo()
      content = '''\
#!/bin/bash
echo kiwi.sh ${1+"$@"}
exit 0
'''
      r.add_file('fruits/kiwi.sh', content, mode = 0o0755)
      r.push('origin', 'master')
      r.tag('1.0.0')
      r.push_tag('1.0.0')
      rv = git_util.repo_run_script(r.address, 'fruits/kiwi.sh', [ 'arg1', 'arg2' ], False, False)
      self.assertEqual( 0, rv.exit_code )
      self.assertEqual( 'kiwi.sh arg1 arg2', rv.stdout.strip() )
    
  def test_repo_run_script_dry_run(self):
    with env_override.temp_home() as env:
      git_unit_test.set_identity()
      r = git_temp_repo()
      content = '''\
#!/bin/bash
echo kiwi.sh ${1+"$@"}
exit 0
'''
      r.add_file('fruits/kiwi.sh', content, mode = 0o0755)
      r.push('origin', 'master')
      r.tag('1.0.0')
      r.push_tag('1.0.0')
      rv = git_util.repo_run_script(r.address, 'fruits/kiwi.sh', [ 'arg1', 'arg2' ], False, True)
      self.assertEqual( None, rv )

  def test_repo_run_script_push(self):
    with env_override.temp_home() as env:
      git_unit_test.set_identity()
      r1 = git_temp_repo()
      content = '''\
#!/bin/bash
echo yellow > color.txt
git add color.txt
git commit -madd color.txt
exit 0
'''
      r1.add_file('fruits/kiwi.sh', content, mode = 0o0755)
      r1.push('origin', 'master')
      r1.tag('1.0.0')
      r1.push_tag('1.0.0')
      rv = git_util.repo_run_script(r1.address, 'fruits/kiwi.sh', [ 'arg1', 'arg2' ], True, False)
      self.assertEqual( 0, rv.exit_code )

      r2 = r1.make_temp_cloned_repo()
      self.assertEqual( 'yellow', r2.read_file('color.txt').strip() )

  def test_repo_run_scripts_push1(self):
    with env_override.temp_home() as env:
      git_unit_test.set_identity()
      r1 = git_temp_repo()
      content1 = '''\
#!/bin/bash
echo ${1} > color.txt
git add color.txt
git commit -madd color.txt
exit 0
'''
      content2 = '''\
#!/bin/bash
echo ${1} > fruit.txt
git add fruit.txt
git commit -madd fruit.txt
exit 0
'''
      r1.add_file('scripts/script1.sh', content1, mode = 0o0755)
      r1.add_file('scripts/script2.sh', content2, mode = 0o0755)
      r1.push('origin', 'master')
      r1.tag('1.0.0')
      r1.push_tag('1.0.0')
      scripts = [
        git_util.script('scripts/script1.sh', [ 'yellow' ]),
        git_util.script('scripts/script2.sh', [ 'kiwi' ]),
      ]
      results = git_util.repo_run_scripts(r1.address, scripts, True, False)
      self.assertEqual( 0, results[0].exit_code )
      self.assertEqual( 0, results[1].exit_code )

      r2 = r1.make_temp_cloned_repo()
      self.assertEqual( 'yellow', r2.read_file('color.txt').strip() )
      self.assertEqual( 'kiwi', r2.read_file('fruit.txt').strip() )
    
if __name__ == '__main__':
  unit_test.main()
