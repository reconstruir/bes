#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import copy, os, os.path as path
from bes.testing.unit_test import unit_test
from bes.system.os_env import os_env
from bes.system.env_override import env_override
from bes.fs.file_util import file_util
from bes.fs.temp_file import temp_file
from bes.fs.testing.temp_content import temp_content
from bes.env.env_dir import env_dir
from bes.env.env_dir import action
from bes.testing.unit_test_skip import raise_skip_if_not_unix

class test_env_dir(unit_test):

  @classmethod
  def setUpClass(clazz):
    raise_skip_if_not_unix()
  
  _TEST_ITEMS = [
    'file 1.sh "export A=1\n" 644',
    'file 2.sh "export B=2\n" 644',
    'file 3.sh "export C=3\n" 644',
    'file 4.sh "export D=4\n" 644',
    'file 5.sh "export E=5\n" 644',
    'file 6.sh "unset F\n" 644',
  ]
    
  def test_files(self):
    ed = self._make_temp_env_dir(self._TEST_ITEMS)
    self.assertEqual( [ '1.sh', '2.sh', '3.sh', '4.sh', '5.sh', '6.sh' ], ed.files )
  
  def test_files_explicit(self):
    ed = self._make_temp_env_dir(self._TEST_ITEMS, files = [ '1.sh', '3.sh', '5.sh' ])
    self.assertEqual( [ '1.sh', '3.sh', '5.sh' ], ed.files )

  def test_files_not_found(self):
    with self.assertRaises(IOError) as ctx:
      self._make_temp_env_dir(self._TEST_ITEMS, files = [ 'notthere.sh' ])
    
  def test_instructions_set(self):
    ed = self._make_temp_env_dir([
      'file 1.sh "export FOO=1\n" 644',
    ])
    env = {}
    self.assertEqual( [
      ( 'FOO', '1', action.SET ),
    ], ed.instructions({}) )
  
  def test_instructions_path_prepend(self):
    ed = self._make_temp_env_dir([
      'file 1.sh "export PATH=/foo/bin:$PATH\n" 644',
    ])
    env = {
      'PATH': '/usr/bin:/bin',
    }
    self.assertEqual( [
      ( 'PATH', '/foo/bin', action.PATH_PREPEND ),
    ], ed.instructions(env) )
  
  def test_instructions_path_append(self):
    ed = self._make_temp_env_dir([
      'file 1.sh "export PATH=$PATH:/foo/bin\n" 644',
    ])
    env = {
      'PATH': '/usr/bin:/bin',
    }
    self.assertEqual( [
      ( 'PATH', '/foo/bin', action.PATH_APPEND ),
    ], ed.instructions(env) )
  
  def test_instructions_path_remove(self):
    ed = self._make_temp_env_dir([
      'file 1.sh "export PATH=/usr/bin:/bin\n" 644',
    ])
    env = {
      'PATH': '/usr/bin:/my/path:/bin',
    }
    self.assertEqual( [
      ( 'PATH', '/my/path', action.PATH_REMOVE ),
    ], ed.instructions(env) )
  
  def test_foo(self):
    env = {
      'SOMETHINGIMADEUP': 'GOOD',
      'PATH': '/bin:/usr/bin:/my/path:/sbin'
    }
    with env_override(env = env) as tmp_env:
      tmp_dir = self.make_temp_dir()
      temp_content.write_items([
        'file 1.sh "export PATH=/bin:/usr/bin:/sbin\n" 644',
        'file 2.sh "export BAR=orange\n" 644',
        'file 3.sh "export PATH=/a/bin:$PATH\nexport PATH=/b/bin:$PATH\n" 644',
        'file 4.sh "export FOO=kiwi\n" 644',
        'file 5.sh "export PATH=$PATH:/x/bin\nPATH=$PATH:/y/bin\n" 644',
        'file 6.sh "unset SOMETHINGIMADEUP\n" 644',
      ], tmp_dir)
      ed = env_dir(tmp_dir)
      self.assertEqual( [ '1.sh', '2.sh', '3.sh', '4.sh', '5.sh', '6.sh' ], ed.files )
      self.assertEqual( [
        ( 'BAR', 'orange', action.SET ),
        ( 'FOO', 'kiwi', action.SET ),
        ( 'PATH', '/a/bin', action.PATH_PREPEND ),
        ( 'PATH', '/b/bin', action.PATH_PREPEND ),
        ( 'PATH', '/my/path', action.PATH_REMOVE ),
        ( 'PATH', '/x/bin', action.PATH_APPEND ),
        ( 'PATH', '/y/bin', action.PATH_APPEND ),
        ( 'SOMETHINGIMADEUP', None, action.UNSET ),
      ], ed.instructions(tmp_env.to_dict()) )

#      self.assertEqual( {
#        'BAR': 'orange',
#        'FOO': 'kiwi',
#        'PATH': '/b/bin:/a/bin:/x/bin:/y/bin',
#      }, ed.transform_env({}) )
        
#      self.assertEqual( {
#        'BAR': 'orange',
#        'FOO': 'kiwi',
#        'PATH': '/b/bin:/a/bin:/x/bin:/y/bin',
#      }, ed.transform_env({ 'SOMETHINGIMADEUP': 'yes' }) )
#        
#      self.assertEqual( {
#        'BAR': 'orange',
#        'FOO': 'kiwi',
#        'PATH': '/b/bin:/a/bin:/usr/local/bin:/usr/foo/bin:/x/bin:/y/bin',
#      }, ed.transform_env({ 'PATH': '/usr/local/bin:/usr/foo/bin' }) )
        
  def _make_temp_env_dir(self, items, files = None):
    tmp_dir = self.make_temp_dir()
    temp_content.write_items(items, tmp_dir)
    return env_dir(tmp_dir, files = files)

  def test_transform_env_empty(self):
    current_env = {}
    current_env_save = copy.deepcopy(current_env)
    ed = self._make_temp_env_dir([])
    transformed_env = ed.transform_env(current_env)
    self.assertEqual( current_env_save, current_env )
    expected = {
    }
    self.assert_dict_as_text_equal( expected, transformed_env )
  
  def test_transform_env_append(self):
    current_env = {
      'PYTHONPATH': '/p/lib/python',
      'PATH': '/p/bin',
    }
    current_env_save = copy.deepcopy(current_env)
    ed = self._make_temp_env_dir([
      'file 1.sh "export PATH=$PATH:/foo/bin\n" 644',
      'file 2.sh "export PYTHONPATH=$PYTHONPATH:/foo/lib/python\n" 644',
    ])
    transformed_env = ed.transform_env(current_env)
    self.assertEqual( current_env_save, current_env )
    expected = {
      'PATH': '/p/bin:/foo/bin',
      'PYTHONPATH': '/p/lib/python:/foo/lib/python',
    }
    self.assert_dict_as_text_equal( expected, transformed_env )
    
  def test_transform_env_set(self):
    current_env = {}
    ed = self._make_temp_env_dir([
      'file 1.sh "export PATH=$PATH:/foo/bin\n" 644',
      'file 2.sh "export PYTHONPATH=$PYTHONPATH:/foo/lib/python\n" 644',
      'file 3.sh "export %s=$%s:/foo/lib\n" 644' % (os_env.LD_LIBRARY_PATH_VAR_NAME,
                                                    os_env.LD_LIBRARY_PATH_VAR_NAME),
    ])
    transformed_env = ed.transform_env(current_env)
    default_PATH = os_env.default_system_value('PATH')
    self.assertEqual( {
      'PATH': '%s:/foo/bin' % (default_PATH),
      'PYTHONPATH': ':/foo/lib/python',
      os_env.LD_LIBRARY_PATH_VAR_NAME: ':/foo/lib',
    }, transformed_env )

  def test_transform_env_unset(self):
    current_env = {}
    ed = self._make_temp_env_dir([
      'file 1.sh "export FOO=foo\n" 644',
      'file 2.sh "export BAR=bar\n" 644',
      'file 3.sh "unset FOO\n" 644',
    ])
    transformed_env = ed.transform_env(current_env)
    self.assertEqual( {
      'BAR': 'bar',
    }, transformed_env )
    
if __name__ == '__main__':
  unit_test.main()
