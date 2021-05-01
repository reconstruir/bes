#!/usr/bin/env python
# -*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path

from bes.testing.program_unit_test import program_unit_test

class test_properties_file_cli_args(program_unit_test):

  _program = program_unit_test.resolve_program(__file__, '..', '..', '..', '..', 'bin', 'best.py')
  
  def test_set_non_existing_file(self):
    tmp_dir = self.make_temp_dir()
    tmp_file = path.join(tmp_dir, 'foo.yml')
    args = [
      'properties_file',
      'set',
      tmp_file,
      'fruit',
      'kiwi',
    ]
    rv = self.run_program(self._program, args)
    self.assertEqual(0, rv.exit_code)
    expected = '''\
fruit: kiwi
'''
    self.assert_text_file_equal( expected, tmp_file )

  def test_set_existing_file(self):
    content = '''\
fruit: kiwi
'''
    tmp_file = self.make_temp_file(content = content)
    args = [
      'properties_file',
      'set',
      tmp_file,
      'fruit',
      'apple',
    ]
    rv = self.run_program(self._program, args)
    self.assertEqual(0, rv.exit_code)
    expected = '''\
fruit: apple
'''
    self.assert_text_file_equal( expected, tmp_file )

  def test_set_value_nonexistent_file(self):
    tmp = self.make_temp_file(suffix = '.yml')
    args = [
      'properties_file',
      'set',
      tmp,
      'fruit',
      'kiwi',
    ]
    rv = self.run_program(self._program, args)
    self.assertEqual( 0, rv.exit_code )
    expected = '''\
fruit: kiwi
'''
    self.assert_text_file_equal( expected, tmp )
    
  def test_set_value_existing_file(self):
    content = '''\
fruit: kiwi
'''
    tmp = self.make_temp_file(content = content, suffix = '.yml')
    args = [
      'properties_file',
      'set',
      tmp,
      'fruit',
      'apple',
    ]
    rv = self.run_program(self._program, args)
    self.assertEqual( 0, rv.exit_code )
    expected = '''\
fruit: apple
'''
    self.assert_text_file_equal( expected, tmp )
    
  def test_get_value_existing_file(self):
    content = '''\
fruit: kiwi
'''
    tmp = self.make_temp_file(content = content, suffix = '.yml')
    args = [
      'properties_file',
      'get',
      tmp,
      'fruit',
    ]
    rv = self.run_program(self._program, args)
    self.assertEqual( 0, rv.exit_code )
    self.assertEqual( 'kiwi', rv.output.strip() )

  def test_bump_version(self):
    content = '''\
ver: 1.2.3
'''
    tmp = self.make_temp_file(content = content, suffix = '.yml')
    args = [
      'properties_file',
      'bump_version',
      tmp,
      'ver',
    ]
    rv = self.run_program(self._program, args)
    self.assertEqual( 0, rv.exit_code )
    expected = '''\
ver: 1.2.4
'''
    self.assert_text_file_equal( expected, tmp )
    
  def test_bump_version_major(self):
    content = '''\
ver: 1.2.3
'''
    tmp = self.make_temp_file(content = content, suffix = '.yml')
    args = [
      'properties_file',
      'bump_version',
      '--component', 'major',
      tmp,
      'ver',
    ]
    rv = self.run_program(self._program, args)
    self.assertEqual( 0, rv.exit_code )
    expected = '''\
ver: 2.2.3
'''
    self.assert_text_file_equal( expected, tmp )
    
if __name__ == '__main__':
  program_unit_test.main()
