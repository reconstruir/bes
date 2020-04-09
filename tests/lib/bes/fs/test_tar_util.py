#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os, os.path as path, tarfile

from bes.fs.file_find import file_find
from bes.fs.file_util import file_util
from bes.fs.tar_util import tar_util
from bes.docker.docker import is_running_under_docker_override_func
from bes.system.host_override import host_override_func
from bes.system.host_info import host_info
from bes.system.env_override import env_override
from bes.system.env_var import os_env_var

from bes.testing.unit_test import unit_test
from bes.testing.unit_test_skip import raise_skip_if_not_unix

class test_tar_util(unit_test):

  __unit_test_data_dir__ = '${BES_TEST_DATA_DIR}/lib/bes/fs/tar_util'

  @classmethod
  def setUpClass(clazz):
    raise_skip_if_not_unix()
  
  def test_copy_tree(self):
    self.maxDiff = None
    src_tmp_dir = self.make_temp_dir(suffix = '.src_dir')
    dst_tmp_dir = self.make_temp_dir(suffix = '.dst_dir')
    with tarfile.open(self.data_path('test.tar'), mode = 'r') as f:
      f.extractall(path = src_tmp_dir)
    tar_util.copy_tree(src_tmp_dir, dst_tmp_dir)
    
    expected_files = [
      self.p('1'),
      self.p('1/2'),
      self.p('1/2/3'),
      self.p('1/2/3/4'),
      self.p('1/2/3/4/5'),
      self.p('1/2/3/4/5/apple.txt'),
      self.p('1/2/3/4/5/kiwi.txt'),
      self.p('bar.txt'),
      self.p('empty'),
      self.p('foo.txt'),
      self.p('kiwi_link.txt'),
    ]
    actual_files = file_find.find(dst_tmp_dir, file_type = file_find.ANY)
    self.assertEqual( expected_files, actual_files )
    
  def test_copy_tree_and_excludes(self):
    self.maxDiff = None
    src_tmp_dir = self.make_temp_dir(suffix = '.src_dir')
    dst_tmp_dir = self.make_temp_dir(suffix = '.dst_dir')
    with tarfile.open(self.data_path('test.tar'), mode = 'r') as f:
      f.extractall(path = src_tmp_dir)
    tar_util.copy_tree(src_tmp_dir, dst_tmp_dir, excludes = [ 'bar.txt', 'foo.txt' ])
    
    expected_files = [
      self.p('1'),
      self.p('1/2'),
      self.p('1/2/3'),
      self.p('1/2/3/4'),
      self.p('1/2/3/4/5'),
      self.p('1/2/3/4/5/apple.txt'),
      self.p('1/2/3/4/5/kiwi.txt'),
      self.p('empty'),
      self.p('kiwi_link.txt'),
    ]
    actual_files = file_find.find(dst_tmp_dir, file_type = file_find.ANY)
    self.assertEqual( expected_files, actual_files )

  def test_copy_tree_spaces_in_filenames(self):
    self.maxDiff = None
    src_tmp_dir = self.make_temp_dir(suffix = '.src_dir-has 2 spaces-')
    dst_tmp_dir = self.make_temp_dir(suffix = '.dst_dir-has 2 spaces-')
    with tarfile.open(self.data_path('test.tar'), mode = 'r') as f:
      f.extractall(path = src_tmp_dir)
    tar_util.copy_tree(src_tmp_dir, dst_tmp_dir)
    
    expected_files = [
      self.p('1'),
      self.p('1/2'),
      self.p('1/2/3'),
      self.p('1/2/3/4'),
      self.p('1/2/3/4/5'),
      self.p('1/2/3/4/5/apple.txt'),
      self.p('1/2/3/4/5/kiwi.txt'),
      self.p('bar.txt'),
      self.p('empty'),
      self.p('foo.txt'),
      self.p('kiwi_link.txt'),
    ]
    actual_files = file_find.find(dst_tmp_dir, file_type = file_find.ANY)
    self.assertEqual( expected_files, actual_files )
    
  def test_extract(self):
    tmp_dir = self.make_temp_dir()
    tar_util.extract(self.data_path('test.tar'), tmp_dir)
    expected_files = [
      self.p('1'),
      self.p('1/2'),
      self.p('1/2/3'),
      self.p('1/2/3/4'),
      self.p('1/2/3/4/5'),
      self.p('1/2/3/4/5/apple.txt'),
      self.p('1/2/3/4/5/kiwi.txt'),
      self.p('bar.txt'),
      self.p('empty'),
      self.p('foo.txt'),
      self.p('kiwi_link.txt'),
    ]
    actual_files = file_find.find(tmp_dir, file_type = file_find.ANY)
    self.assertEqual( expected_files, actual_files )

  def test_extract(self):
    tmp_dir = self.make_temp_dir()
    tar_util.extract(self.data_path('test.tar'), tmp_dir)
    expected_files = [
      self.p('1'),
      self.p('1/2'),
      self.p('1/2/3'),
      self.p('1/2/3/4'),
      self.p('1/2/3/4/5'),
      self.p('1/2/3/4/5/apple.txt'),
      self.p('1/2/3/4/5/kiwi.txt'),
      self.p('bar.txt'),
      self.p('empty'),
      self.p('foo.txt'),
      self.p('kiwi_link.txt'),
    ]
    actual_files = file_find.find(tmp_dir, file_type = file_find.ANY)
    self.assertEqual( expected_files, actual_files )

  @host_override_func(host_info('linux', '3', '10', 'x86_64', 'alpine', 'alpine'))
  @is_running_under_docker_override_func(False)
  def test_extract_alpine_linux_without_docker(self):
    tmp_dir = self.make_temp_dir()
    tar_util.extract(self.data_path('test.tar'), tmp_dir)
    expected_files = [
      self.p('1'),
      self.p('1/2'),
      self.p('1/2/3'),
      self.p('1/2/3/4'),
      self.p('1/2/3/4/5'),
      self.p('1/2/3/4/5/apple.txt'),
      self.p('1/2/3/4/5/kiwi.txt'),
      self.p('bar.txt'),
      self.p('empty'),
      self.p('foo.txt'),
      self.p('kiwi_link.txt'),
    ]
    actual_files = file_find.find(tmp_dir, file_type = file_find.ANY)
    self.assertEqual( expected_files, actual_files )

  @host_override_func(host_info('linux', '3', '10', 'x86_64', 'alpine', 'alpine'))
  @is_running_under_docker_override_func(True)
  def test_extract_alpine_linux_with_docker(self):
    tmp_tar_exe_dir = self.make_temp_dir()
    fail_flag_file = self.make_temp_file(content = 'foo', suffix = '.flag')
    
    fake_tar_content = '''\
#!/bin/bash
${_BES_TAR_EXE} ${1+"$@"}
if [[ -f ${_BES_TAR_FAIL_FLAG} ]]; then
  rm -f ${_BES_TAR_FAIL_FLAG}
  exit 2
fi
rv=$?
exit ${rv}
'''
    tar_exe = file_util.save(path.join(tmp_tar_exe_dir, 'tar'), content = fake_tar_content, mode = 0o0755)
    
    tmp_dir = self.make_temp_dir()
    
    old_path = os_env_var
    with env_override(env = { '_BES_TAR_EXE': tar_util.tar_exe(), '_BES_TAR_FAIL_FLAG': fail_flag_file }) as over:
      os_env_var('PATH').prepend(tmp_tar_exe_dir)
      tar_util.extract(self.data_path('test.tar'), tmp_dir)
      
    expected_files = [
      self.p('1'),
      self.p('1/2'),
      self.p('1/2/3'),
      self.p('1/2/3/4'),
      self.p('1/2/3/4/5'),
      self.p('1/2/3/4/5/apple.txt'),
      self.p('1/2/3/4/5/kiwi.txt'),
      self.p('bar.txt'),
      self.p('empty'),
      self.p('foo.txt'),
      self.p('kiwi_link.txt'),
    ]
    actual_files = file_find.find(tmp_dir, file_type = file_find.ANY)
    self.assertEqual( expected_files, actual_files )
    
if __name__ == '__main__':
  unit_test.main()
