#!/usr/bin/env python3
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.git.git_clone_manager import git_clone_manager as GCM

from bes.git.git_temp_repo import git_temp_repo
from bes.git.git_unit_test import git_temp_home_func

class test_git_clone_manager(unit_test):

  @git_temp_home_func()
  def test_update(self):
    r1 = self._make_repo()
    r1.write_temp_content([
      'file foo.txt "this is foo" 644',
    ])
    r1.add([ 'foo.txt' ])
    r1.commit('add foo.txt', [ 'foo.txt' ])
    r1.push('origin', 'master')

    g = GCM(self.make_temp_dir(suffix = '.gcm.dir'))
    r1b = g.update(r1.address)
    r1b.remove('foo.txt')
    r1b.commit('remove foo.txt', 'foo.txt')
    r1b.push()
            
  def _make_repo(self, remote = True, content = None, prefix = None):
    return git_temp_repo(remote = remote, content = content, prefix = prefix, debug = self.DEBUG)
  
if __name__ == '__main__':
  unit_test.main()
