#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-
#
from bes.testing.unit_test import unit_test
from bes.git.git_attributes_item import git_attributes_item
from bes.git.git_attributes import git_attributes
from bes.git.git_unit_test import git_temp_home_func
from bes.key_value.key_value import key_value
from bes.key_value.key_value_list import key_value_list

class test_git_attributes(unit_test):

  @git_temp_home_func()
  def test___str__(self):
    l = git_attributes([
      git_attributes_item('*.png', key_value_list.parse('filter=lfs diff=lfs merge=lfs') + [ key_value('text', False) ]),
      git_attributes_item('*.txt', key_value_list([ key_value('text', True) ])),
    ])
    self.assertEqual( '''\
*.png filter=lfs diff=lfs merge=lfs -text
*.txt text
''', str(l) )
    
  @git_temp_home_func()
  def test_parse(self):
    text = '''\
*.png filter=lfs diff=lfs merge=lfs -text
*.txt text
'''
    expected = git_attributes([
      git_attributes_item('*.png', key_value_list.parse('filter=lfs diff=lfs merge=lfs') + [ key_value('text', False) ]),
      git_attributes_item('*.txt', key_value_list([ key_value('text', True) ])),
    ])
    
    self.assertEqual( expected, git_attributes.parse(text) )
    
if __name__ == '__main__':
  unit_test.main()
