#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple
import os.path as path

from bes.env.env_dir import env_dir
from bes.shell_framework.shell_framework import shell_framework
from bes.shell_framework.shell_framework_options import shell_framework_options
from bes.fs.file_find import file_find
from bes.fs.file_util import file_util
from bes.fs.tar_util import tar_util
from bes.fs.temp_file import temp_file
from bes.system.os_env import os_env
from bes.testing.unit_test import unit_test
from bes.git.git_temp_repo import git_temp_repo
from bes.git.git_unit_test import git_temp_home_func
from bes.testing.unit_test_class_skip import unit_test_class_skip

class test_shell_framework(unit_test):

  @classmethod
  def setUpClass(clazz):
    unit_test_class_skip.raise_skip_if_not_unix()

  @git_temp_home_func()
  def test_latest_revision(self):
    test = self._make_test_shell_framework()
    self.assertEqual( None, test.framework.latest_revision )
    test.repo.tag('1.2.3', push = True)
    self.assertEqual( '1.2.3', test.framework.latest_revision )
    test.repo.tag('1.2.2', push = True)
    self.assertEqual( '1.2.3', test.framework.latest_revision )

  @git_temp_home_func()
  def test_current_revision(self):
    test = self._make_test_shell_framework()
    test.repo.tag('1.2.3', push = True)
    test.repo.tag('1.2.4', push = True)
    self.assertEqual( None, test.framework.current_revision )
    test.framework.update('1.2.3')
    self.assertEqual( '1.2.3', test.framework.current_revision )
    test.framework.update('1.2.4')
    self.assertEqual( '1.2.4', test.framework.current_revision )

  @git_temp_home_func()
  def test_current_revision(self):
    test = self._make_test_shell_framework()
    test.repo.tag('1.2.3', push = True)
    test.repo.tag('1.2.4', push = True)
    self.assertEqual( None, test.framework.current_revision )
    test.framework.update('1.2.3')
    self.assertEqual( '1.2.3', test.framework.current_revision )
    test.framework.update('1.2.4')
    self.assertEqual( '1.2.4', test.framework.current_revision )
    
  @git_temp_home_func()
  def test_update(self):
    test = self._make_test_shell_framework()
    test.repo.tag('1.2.3', push = True)
    test.framework.update('1.2.3')
    self.assertEqual( '1.2.3', test.framework.current_revision )
    files = file_find.find(test.tmp_dir)
    self.assertEqual( [
      'bes_shell_framework/bes_bash.bash',
      'bes_shell_framework_revision.txt',
    ], files )

  @git_temp_home_func()
  def test_update_to_latest(self):
    test = self._make_test_shell_framework()
    test.repo.tag('1.2.3', push = True)
    test.repo.tag('1.2.4', push = True)
    test.framework.update('latest')
    self.assertEqual( '1.2.4', test.framework.current_revision )
    
  @git_temp_home_func()
  def test_use_framework(self):
    test = self._make_test_shell_framework()
    test.repo.tag('1.2.3', push = True)
    test.framework.update('1.2.3')
    my_script_content = '''
_this_file="$( command readlink "$BASH_SOURCE" )" || _this_file="$BASH_SOURCE"
_root="${_this_file%/*}"
if [ "$_root" == "$_this_file" ]; then
  _root=.
fi
_WHERE="$( command cd -P "$_root" > /dev/null && command pwd -P )"
unset _this_file
unset _root
source ${_WHERE}/bes_shell_framework/bes_bash.bash
bes_env_path_append PATH /foo/bin
'''
    my_script_path = path.join(test.tmp_dir, 'my_script.sh')
    file_util.save(my_script_path, content = my_script_content, mode = 0o755)
    
    ed = env_dir(test.tmp_dir, files = [ 'my_script.sh' ])
    flat_system_path = path.pathsep.join(os_env.DEFAULT_SYSTEM_PATH)
    expected = {
      'PATH': f'{flat_system_path}:/foo/bin',
    }
    actual = ed.transform_env({ 'PATH': flat_system_path })
    self.assertEqual( expected, actual )

  @classmethod
  def _make_test_repo(clazz):
    repo = git_temp_repo(debug = clazz.DEBUG)
    src_dir = path.normpath(path.join(path.dirname(__file__), '../../../../bes_bash'))
    dst_dir = path.join(repo.root, 'bash/bes_bash_one_file')
    tar_util.copy_tree(src_dir, dst_dir)
    repo.add([ 'bash' ])
    repo.commit('add', [ 'bash' ])
    repo.push('-u', 'origin', 'master')
    return repo

  _test_framework = namedtuple('_test_framework', 'framework,repo,tmp_dir')
  def _make_test_shell_framework(self, **kargs):
    tmp_dir = self.make_temp_dir()
    repo = self._make_test_repo()
    options = shell_framework_options(address = repo.address,
                                      dest_dir = tmp_dir,
                                      **kargs)
    sf = shell_framework(options = options)
    return self._test_framework(sf, repo, tmp_dir)
    
if __name__ == '__main__':
  unit_test.main()
