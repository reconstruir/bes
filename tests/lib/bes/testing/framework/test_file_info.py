#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.testing.unit_test import unit_test
from bes.testing.framework.config_env import config_env
from bes.testing.framework.file_info import file_info as FI
from bes.fs.temp_file import temp_file
from bes.git.git import git
from bes.git.git_temp_repo import git_temp_repo
from bes.testing.unit_test_class_skip import unit_test_class_skip

from example_data import example_data

class test_file_info(unit_test):

  @classmethod
  def setUpClass(clazz):
    unit_test_class_skip.raise_skip('broken')
  
  def test_filename(self):
    tmp_dir = example_data.make_temp_content(delete = not self.DEBUG)
    ce = config_env(tmp_dir)
    a = FI(ce, path.join(tmp_dir, 'orange/lib/orange/common/orange_util.py'))
    self.assertEqual( path.join(tmp_dir, 'orange/lib/orange/common/orange_util.py'), a.filename )
  
  def test_relative_filename(self):
    tmp_dir = example_data.make_temp_content(delete = not self.DEBUG)
    ce = config_env(tmp_dir)
    a = FI(ce, path.join(tmp_dir, 'orange/lib/orange/common/orange_util.py'))
    self.assertEqual( 'lib/orange/common/orange_util.py', a.relative_filename )
  
  def test_config(self):
    tmp_dir = example_data.make_temp_content(delete = not self.DEBUG)
    ce = config_env(tmp_dir)
    a = FI(ce, path.join(tmp_dir, 'orange/lib/orange/common/orange_util.py'))
    self.assertEqual( ce.config_for_name('orange'), a.config )
  
  def test_git_root(self):
    tmp_dir = example_data.make_temp_content(delete = not self.DEBUG)
    ce = config_env(tmp_dir)
    a = FI(ce, path.join(tmp_dir, 'orange/lib/orange/common/orange_util.py'))
    self.assertEqual( git.root(path.join(tmp_dir, 'orange/lib/orange/common/orange_util.py')), a.git_root )

  def test_git_tracked(self):
    tmp_dir = example_data.make_temp_content(delete = not self.DEBUG)
    r = git_temp_repo(content = [ 'file lib/foo/foo.py "def foo(): return 666\n" 644' ])
    ce = config_env(r.root)
    a = FI(ce, path.join(r.root, 'lib/foo/foo.py'))
    #self.assertEqual( r.root, a.git_root )
    self.assertEqual( True, a.git_tracked )
    
  def test_not_git_tracked(self):
    tmp_dir = example_data.make_temp_content(delete = not self.DEBUG)
    ce = config_env(tmp_dir)
    a = FI(ce, temp_file.make_temp_file(content = 'def foo(): return 666\n'))
    self.assertEqual( None, a.git_root )
    self.assertEqual( False, a.git_tracked )
    self.assertEqual( None, a.config )

  def test_inspection(self):
    a = self._make_file_info('orange/tests/lib/orange/common/test_orange_util.py')
    for x in a.inspection:
      print ('INSP: %s' % (str(x)))
    
  def _make_file_info(self, filename):
    tmp_dir = example_data.make_temp_content(delete = not self.DEBUG)
    return FI(config_env(tmp_dir), path.join(tmp_dir, filename))
    
if __name__ == '__main__':
  unit_test.main()
    
