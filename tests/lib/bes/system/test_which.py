#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os, os.path as path, unittest

from bes.fs.file_util import file_util
from bes.system.env_override import env_override
from bes.system.host import host
from bes.system.which import which
from bes.testing.unit_test import unit_test
from bes.testing.unit_test_skip import skip_if

class test_which(unit_test):
    
  @skip_if(not host.is_unix(), 'not unix')
  def test_which_unix(self):
    'Test which() in unix.'
    tmp_dir = self.make_temp_dir()
    bin_dir = path.join(tmp_dir, 'bin')
    content = '!#/bin/bash\nechoecho kiwi\nexit 0\n'
    temp_exe = file_util.save(path.join(bin_dir, 'fruit_kiwi_tool'), content = content, mode = 0o0755)
    self.assertEqual( None, which.which('fruit_kiwi_tool') )
    with env_override.path_append(bin_dir) as env:
      expected_path = path.join(bin_dir, 'fruit_kiwi_tool')
      self.assertEqual( expected_path, which.which('fruit_kiwi_tool') )

  @skip_if(not host.is_windows(), 'not windows')
  def test_which_unix(self):
    'Test which() in unix.'
    tmp_dir = self.make_temp_dir()
    bin_dir = path.join(tmp_dir, 'bin')
    content = '@echo off\n\recho kiwi\n\rexit 0\n\r'
    temp_bat = file_util.save(path.join(bin_dir, 'fruit_kiwi_tool.bat'), content = content, mode = 0o0755)
    self.assertEqual( None, which.which('fruit_kiwi_tool.bat') )
    with env_override.path_append(bin_dir) as env:
      expected_path = path.join(bin_dir, 'fruit_kiwi_tool.bat')
      self.assertEqual( expected_path, which.which('fruit_kiwi_tool.bat') )
      self.assertEqual( expected_path, which.which('fruit_kiwi_tool') )
      
if __name__ == '__main__':
  unit_test.main()
