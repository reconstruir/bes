#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os, os.path as path, unittest

from bes.testing.unit_test import unit_test
from bes.fs.file_util import file_util
from bes.system.env_override import env_override

from bes.system.which import which

class test_which(unit_test):
    
  def test_which(self):
    'Test which()  Looks like a windows only test but works on unix as well.'
    tmp_dir = self.make_temp_dir()
    bin_dir = path.join(tmp_dir, 'bin')
    content = '@echo off\n\recho kiwi\n\rexit 0\n\r'
    temp_bat = file_util.save(path.join(bin_dir, 'kiwi_tool.bat'), content = content, mode = 0o0755)
    self.assertEqual( None, which.which('kiwi_tool.bat') )
    with env_override.path_append(bin_dir) as env:
      expected_path = path.join(bin_dir, 'kiwi_tool.bat')
      self.assertEqual( expected_path, which.which('kiwi_tool.bat') )
    
if __name__ == '__main__':
  unit_test.main()
