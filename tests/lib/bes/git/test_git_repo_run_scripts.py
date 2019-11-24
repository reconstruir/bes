#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path
from bes.testing.unit_test import unit_test
from bes.git.git_util import git_util
from bes.git.git_temp_repo import git_temp_repo
from bes.system.host import host
from bes.git.git_unit_test import git_temp_home_func
from bes.git.git_repo_script_options import git_repo_script_options

class test_git_repo_run_scripts(unit_test):
  
  @git_temp_home_func()
  def test_repo_run_script_one(self):
    r = git_temp_repo(debug = self.DEBUG)
    if host.is_windows():
      script = self.xp_path('fruits/kiwi.bat')
      content = '''\
@echo off
echo {} %*
exit 0
'''.format(script)
    elif host.is_unix():
      script = self.xp_path('fruits/kiwi.sh')
      content = '''\
#!/bin/bash
echo {} ${{1+"$@"}}
exit 0
'''.format(script)
    else:
      assert False
    xp_script = self.xp_path(script)
    r.add_file(self.xp_path(xp_script), content, mode = 0o0755)
    r.push('origin', 'master')
    r.tag('1.0.0')
    r.push_tag('1.0.0')
    scripts = [
      git_util.script(xp_script, [ 'arg1', 'arg2' ]),
    ]
    rv = git_util.repo_run_scripts(r.address, scripts)
    self.assertEqual( 1, len(rv.results) )
    self.assertEqual( '{} arg1 arg2'.format(xp_script), rv.results[0].stdout.strip() )
    
  @git_temp_home_func()
  def test_repo_run_script_one_dry_run(self):
    r = git_temp_repo(debug = self.DEBUG)
    if host.is_windows():
      script = self.xp_path('fruits/kiwi.bat')
      content = '''\
@echo off
echo {} %*
exit 0
'''.format(script)
    elif host.is_unix():
      script = self.xp_path('fruits/kiwi.sh')
      content = '''\
#!/bin/bash
echo {} ${{1+"$@"}}
exit 0
'''.format(script)
    else:
      assert False
    xp_script = self.xp_path(script)
    r.add_file(self.xp_path(xp_script), content, mode = 0o0755)
    r.push('origin', 'master')
    r.tag('1.0.0')
    r.push_tag('1.0.0')
    options = git_repo_script_options(dry_run = True)
    scripts = [
      git_util.script(xp_script, [ 'arg1', 'arg2' ]),
    ]
    rv = git_util.repo_run_scripts(r.address, scripts, options = options)
    self.assertEqual( [ None ], rv.results )

  @git_temp_home_func()
  def test_repo_run_script_push(self):
    r1 = git_temp_repo(debug = self.DEBUG)
    if host.is_windows():
      script = self.xp_path('fruits/kiwi.bat')
      content = '''\
@echo off
echo yellow > color.txt
git add color.txt
git commit -madd color.txt
exit 0
'''
    elif host.is_unix():
      script = self.xp_path('fruits/kiwi.sh')
      content = '''\
#!/bin/bash
echo yellow > color.txt
git add color.txt
git commit -madd color.txt
exit 0
'''
    else:
      assert False
    xp_script = self.xp_path(script)
    r1.add_file(xp_script, content, mode = 0o0755)
    r1.push('origin', 'master')
    r1.tag('1.0.0')
    r1.push_tag('1.0.0')
    options = git_repo_script_options(push = True)
    scripts = [
      git_util.script(xp_script, [ 'arg1', 'arg2' ]),
    ]
    rv = git_util.repo_run_scripts(r1.address, scripts, options = options)
    self.assertEqual( 1, len(rv.results) )

    r2 = r1.make_temp_cloned_repo()
    self.assertEqual( 'yellow', r2.read_file('color.txt').strip() )

  @git_temp_home_func()
  def test_repo_run_scripts_push(self):
    r1 = git_temp_repo(debug = self.DEBUG)
    if host.is_windows():
      script1 = self.xp_path('scripts/script1.bat')
      script2 = self.xp_path('scripts/script2.bat')
      content1 = '''\
@echo off
echo %1% > color.txt
git add color.txt
git commit -madd color.txt
exit 0
'''
      content2 = '''\
@echo off
echo %1% > fruit.txt
git add fruit.txt
git commit -madd fruit.txt
exit 0
'''
    elif host.is_unix():
      script1 = self.xp_path('scripts/script1.sh')
      script2 = self.xp_path('scripts/script2.sh')
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
    else:
      assert False
    r1.add_file(script1, content1, mode = 0o0755)
    r1.add_file(script2, content2, mode = 0o0755)
    r1.push('origin', 'master')
    r1.tag('1.0.0')
    r1.push_tag('1.0.0')
    scripts = [
      git_util.script(script1, [ 'yellow' ]),
      git_util.script(script2, [ 'kiwi' ]),
    ]
    options = git_repo_script_options(push = True)
    rv = git_util.repo_run_scripts(r1.address, scripts, options = options)

    r2 = r1.make_temp_cloned_repo()
    self.assertEqual( 'yellow', r2.read_file('color.txt').strip() )
    self.assertEqual( 'kiwi', r2.read_file('fruit.txt').strip() )

  @git_temp_home_func()
  def test_repo_run_script_bump_tag(self):
    r1 = git_temp_repo(debug = self.DEBUG)
    if host.is_windows():
      script = 'nothing.bat'
      content = '''\
@echo off
exit 0
'''.format(script)
    elif host.is_unix():
      script = './nothing.sh'
      content = '''\
#!/bin/bash
exit 0
'''.format(script)
    else:
      assert False
    xp_script = self.xp_path(script)
    r1.add_file(xp_script, content, mode = 0o0755)
    r1.push('origin', 'master')
    r1.tag('1.0.0')
    r1.push_tag('1.0.0')
    options = git_repo_script_options(bump_tag_component = 'revision')
    scripts = [
      git_util.script(xp_script, []),
    ]
    rv = git_util.repo_run_scripts(r1.address, scripts, options = options)
    self.assertEqual( 1, len(rv.results) )

    r2 = r1.make_temp_cloned_repo()
    self.assertEqual( '1.0.1', r2.greatest_local_tag() )

    options = git_repo_script_options(bump_tag_component = 'major')
    scripts = [
      git_util.script(xp_script, []),
    ]
    rv = git_util.repo_run_scripts(r1.address, scripts, options = options)
    self.assertEqual( 1, len(rv.results) )
    self.assertEqual( '2.0.1', r2.greatest_remote_tag() )
    
if __name__ == '__main__':
  unit_test.main()
