#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.testing.unit_test import unit_test
from bes.fs import file_util, temp_file
from bes.env import shell_framework
from bes.env.env_dir import env_dir
from bes.system import os_env
from bes.fs.testing import temp_content

class test_shell_framework(unit_test):

  def test_extract(self):
    tmp_dir = temp_file.make_temp_dir(delete = False)
    ef = shell_framework()
    ef.extract(tmp_dir)
    self.assertTrue( path.exists(path.join(tmp_dir, 'env/bes_framework.sh')) )
    
  def test_use_framework(self):
    tmp_dir = temp_file.make_temp_dir(delete = False)
    ef = shell_framework()
    ef.extract(tmp_dir)
    env_path = path.join(tmp_dir, 'env')

    my_script_content = '''
_this_file="$( command readlink "$BASH_SOURCE" )" || _this_file="$BASH_SOURCE"
_root="${_this_file%/*}"
if [ "$_root" == "$_this_file" ]; then
  _root=.
fi
_FOO="$( command cd -P "$_root" > /dev/null && command pwd -P )"
unset _this_file
unset _root
source ${_FOO}/bes_framework.sh
bes_env_path_append PATH /foo/bin
'''
    my_script_path = path.join(env_path, 'my_script.sh')
    file_util.save(my_script_path, content = my_script_content)
    
    ed = env_dir(env_path, files = [ 'my_script.sh' ])
    expected = {
      'PATH': '%s:/foo/bin' % (os_env.DEFAULT_SYSTEM_PATH),
    }
    actual = ed.transform_env({ 'PATH': os_env.DEFAULT_SYSTEM_PATH })
    self.assertEqual( expected, actual )
    
if __name__ == '__main__':
  unit_test.main()
