#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.testing.unit_test import unit_test
from bes.testing.framework import config_env, file_info as FI
from bes.fs import temp_file
from bes.git import git, repo, temp_git_repo
from bes.testing.unit_test.unit_test_skip import raise_skip
  
class test_file_info(unit_test):

  @classmethod
  def setUpClass(clazz):
    raise_skip('broken')
  
  __unit_test_data_dir__ = '${BES_TEST_DATA_DIR}/bes.testing/framework'

  def test_filename(self):
    ce = config_env(self.data_dir())
    a = FI(ce, self.data_path('orange/lib/orange/common/orange_util.py'))
    self.assertEqual( self.data_path('orange/lib/orange/common/orange_util.py'), a.filename )
  
  def test_relative_filename(self):
    ce = config_env(self.data_dir())
    a = FI(ce, self.data_path('orange/lib/orange/common/orange_util.py'))
    self.assertEqual( 'lib/orange/common/orange_util.py', a.relative_filename )
  
  def test_config(self):
    ce = config_env(self.data_dir())
    a = FI(ce, self.data_path('orange/lib/orange/common/orange_util.py'))
    self.assertEqual( ce.config_for_name('orange'), a.config )
  
  def test_git_root(self):
    ce = config_env(self.data_dir())
    a = FI(ce, self.data_path('orange/lib/orange/common/orange_util.py'))
    self.assertEqual( git.root(self.data_path('orange/lib/orange/common/orange_util.py')), a.git_root )

  def test_git_tracked(self):
    r = temp_git_repo.make_temp_repo(content = [ 'file lib/foo/foo.py "def foo(): return 666\n" 644' ])
    ce = config_env(r.root)
    a = FI(ce, path.join(r.root, 'lib/foo/foo.py'))
    #self.assertEqual( r.root, a.git_root )
    self.assertEqual( True, a.git_tracked )
    
  def test_not_git_tracked(self):
    ce = config_env(self.data_dir())
    a = FI(ce, temp_file.make_temp_file(content = 'def foo(): return 666\n'))
    self.assertEqual( None, a.git_root )
    self.assertEqual( False, a.git_tracked )
    self.assertEqual( None, a.config )

  def test_inspection(self):
    a = self._make_file_info('orange/tests/lib/orange/common/test_orange_util.py')
    for x in a.inspection:
      print ('INSP: %s' % (str(x)))
    
  def _make_file_info(self, filename):
    return FI(config_env(self.data_dir()), self.data_path(filename))
    
if __name__ == '__main__':
  unit_test.main()
    
