#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.testing.unit_test import unit_test
from bes.fs.file_util import file_util
from bes.fs.temp_file import temp_file
from bes.env.shell_framework import shell_framework
from bes.env.env_dir import env_dir
from bes.system.os_env import os_env
from bes.fs.testing import temp_content

class test_shell_framework(unit_test):

  DEBUG = unit_test.DEBUG

  def test_extract(self):
    tmp_dir = temp_file.make_temp_dir(delete = not self.DEBUG)
    ef = shell_framework()
    ef.extract(tmp_dir)
    self.assertTrue( path.exists(path.join(tmp_dir, 'bes_shell.sh')) )
  
  def test_use_framework(self):
    tmp_dir = temp_file.make_temp_dir(delete = not self.DEBUG)
    if self.DEBUG:
      print('tmp_dir: %s' % (tmp_dir))
    ef = shell_framework()
    ef.extract(tmp_dir)

    my_script_content = '''
_this_file="$( command readlink "$BASH_SOURCE" )" || _this_file="$BASH_SOURCE"
_root="${_this_file%/*}"
if [ "$_root" == "$_this_file" ]; then
  _root=.
fi
_WHERE="$( command cd -P "$_root" > /dev/null && command pwd -P )"
unset _this_file
unset _root
source ${_WHERE}/bes_shell.sh
bes_env_path_append PATH /foo/bin
'''
    my_script_path = path.join(tmp_dir, 'my_script.sh')
    file_util.save(my_script_path, content = my_script_content, mode = 0o755)
    
    ed = env_dir(tmp_dir, files = [ 'my_script.sh' ])
    expected = {
      'PATH': '%s:/foo/bin' % (os_env.DEFAULT_SYSTEM_PATH),
    }
    actual = ed.transform_env({ 'PATH': os_env.DEFAULT_SYSTEM_PATH })
    self.assertEqual( expected, actual )
    
if __name__ == '__main__':
  unit_test.main()
