#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path
import multiprocessing

from bes.testing.unit_test import unit_test
from bes.git.git_util import git_util
from bes.git.git_repo import git_repo
from bes.git.git_temp_repo import git_temp_repo
from bes.system.host import host
from bes.git.git_unit_test import git_temp_home_func
from bes.git.git_repo_script_options import git_repo_script_options

class test_git_repo_run_scripts(unit_test):
  
  @git_temp_home_func()
  def test_one_script(self):
    r = git_temp_repo(debug = self.DEBUG)
    if host.is_windows():
      script = self.native_filename('fruits/kiwi.bat')
      content = '''\
@echo off
echo {} %*
exit 0
'''.format(script)
    elif host.is_unix():
      script = self.native_filename('fruits/kiwi.sh')
      content = '''\
#!/bin/bash
echo {} ${{1+"$@"}}
exit 0
'''.format(script)
    else:
      assert False
    xp_script = self.native_filename(script)
    r.add_file(self.native_filename(xp_script), content, mode = 0o0755)
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
  def test_one_script_with_dry_run(self):
    r = git_temp_repo(debug = self.DEBUG)
    if host.is_windows():
      script = self.native_filename('fruits/kiwi.bat')
      content = '''\
@echo off
echo {} %*
exit 0
'''.format(script)
    elif host.is_unix():
      script = self.native_filename('fruits/kiwi.sh')
      content = '''\
#!/bin/bash
echo {} ${{1+"$@"}}
exit 0
'''.format(script)
    else:
      assert False
    xp_script = self.native_filename(script)
    r.add_file(self.native_filename(xp_script), content, mode = 0o0755)
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
  def test_one_script_with_push(self):
    r1 = git_temp_repo(debug = self.DEBUG)
    if host.is_windows():
      script = self.native_filename('fruits/kiwi.bat')
      content = '''\
@echo off
echo yellow > color.txt
git add color.txt
git commit -madd color.txt
exit 0
'''
    elif host.is_unix():
      script = self.native_filename('fruits/kiwi.sh')
      content = '''\
#!/bin/bash
echo yellow > color.txt
git add color.txt
git commit -madd color.txt
exit 0
'''
    else:
      assert False
    xp_script = self.native_filename(script)
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
  def test_many_scripts_with_push(self):
    r1 = git_temp_repo(debug = self.DEBUG)
    if host.is_windows():
      script1 = self.native_filename('scripts/script1.bat')
      script2 = self.native_filename('scripts/script2.bat')
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
      script1 = self.native_filename('scripts/script1.sh')
      script2 = self.native_filename('scripts/script2.sh')
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
  def test_one_script_with_bump_tag(self):
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
    xp_script = self.native_filename(script)
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

  _FRUITS = [
    'apple',
    'blueberry',
    'kiwi',
    'lemon',
    'melon',
    'orange',
    'papaya',
    'pineapple',
    'watermelon',
  ]

  @staticmethod
  def _worker_test_push_conflict(fruit, address, xp_script):
    options = git_repo_script_options(push = True, push_with_rebase = True)
    scripts = [
      git_util.script(xp_script, [ fruit ]),
    ]
    rv = git_util.repo_run_scripts(address, scripts, options = options)
    print('rv: {}'.format(str(rv)))
      
    #tmp_dir = self.make_temp_dir()
    #content = self._make_content(fruit)
    #repo = git_repo(tmp_dir, address = r2.address)
    #repo.clone_or_pull()
    #repo.add_file(fruit, content = fruit, commit = True)
    #repo.push_with_rebase(num_tries = 10, retry_wait_seconds = 0.250)
    return 0
  
  @git_temp_home_func()
  def test_push_conflict(self):
    r1 = git_temp_repo(debug = self.DEBUG)
    if host.is_windows():
      script = self.native_filename('fruits/kiwi.bat')
      content = '''\
@echo off
echo %1 > %1
git add %1
git commit -m"add %1" %1
exit 0
'''
    elif host.is_unix():
      script = self.native_filename('fruits/kiwi.sh')
      content = '''\
#!/bin/bash
echo ${1} > ${1}
git add ${1}
git commit -m"add ${1}" ${1}
exit 0
'''
    else:
      assert False
    xp_script = self.native_filename(script)
    r1.add_file(self.native_filename(xp_script), content, mode = 0o0755)
    r1.push('origin', 'master')

    jobs = []
    for fruit in self._FRUITS:
      p = multiprocessing.Process(target = self._worker_test_push_conflict, args = ( fruit, r1.address, xp_script ) )
      jobs.append(p)
      p.start()

    for job in jobs:
      job.join()

    r2 = git_repo(self.make_temp_dir(), address = r1.address)
    r2.clone_or_pull()

    self.assertEqual( {
      xp_script, 
      'apple',
      'blueberry',
      'kiwi',
      'lemon',
      'melon',
      'orange',
      'papaya',
      'pineapple',
      'watermelon',
    }, set(r2.find_all_files()) )

    '''
    scripts = [
      git_util.script(xp_script, [ 'arg1', 'arg2' ]),
    ]
    rv = git_util.repo_run_scripts(r.address, scripts)
    self.assertEqual( 1, len(rv.results) )
    self.assertEqual( '{} arg1 arg2'.format(xp_script), rv.results[0].stdout.strip() )
    '''
    
if __name__ == '__main__':
  unit_test.main()
