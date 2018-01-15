#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.testing.unit_test import unit_test
from bes.fs import file_search

class test_file_search(unit_test):

  __unit_test_data_dir__ = '../../../../test_data/bes.fs/file_search'
  
  def test_search_string(self):
    content = '''\
this is foo
upper Foo
more is bar
baz is next
foobar is mixed
bar_ has under
!bar#
'''
    actual = file_search.search_string(content, 'foo')
    expected = [
      ( '<unknown>', 1, 'foo', 'this is foo', ( 8, 11 ) ),
      ( '<unknown>', 5, 'foo', 'foobar is mixed', ( 0, 3 ) ),
    ]
    self.assertEqual( expected, actual )

  def test_search_string_ignore_case(self):
    content = '''\
this is foo
upper Foo
more is bar
baz is next
foobar is mixed
bar_ has under
!bar#
'''
    actual = file_search.search_string(content, 'foo', ignore_case = True)
    expected = [
      ( '<unknown>', 1, 'foo', 'this is foo', ( 8, 11 ) ),
      ( '<unknown>', 2, 'foo', 'upper Foo', ( 6, 9 ) ),
      ( '<unknown>', 5, 'foo', 'foobar is mixed', ( 0, 3 ) ),
    ]
    self.assertEqual( expected, actual )

  def test_search_string_word_boundary(self):
    content = '''\
this is foo
upper Foo
more is bar
baz is next
foobar is mixed
bar_ has under
!bar#
'''
    actual = file_search.search_string(content, 'foo', word_boundary = True)
    expected = [
      ( '<unknown>', 1, 'foo', 'this is foo', ( 8, 11 ) ),
    ]
    self.assertEqual( expected, actual )


  def test_search_string_word_boundary_ignore_case(self):
    content = '''\
this is foo
upper Foo
more is bar
baz is next
foobar is mixed
bar_ has under
!bar#
'''
    actual = file_search.search_string(content, 'foo', word_boundary = True, ignore_case = True)
    expected = [
      ( '<unknown>', 1, 'foo', 'this is foo', ( 8, 11 ) ),
      ( '<unknown>', 2, 'foo', 'upper Foo', ( 6, 9 ) ),
    ]
    self.assertEqual( expected, actual )
    
  def test_search_relative(self):
    actual = file_search.search(unicode(self.data_dir()), 'this', relative = True)
    expected = [
      ( 'apple.txt', 1, 'this', 'this is apple', ( 0, 4 ) ),
      ( 'kiwi.txt', 1, 'this', 'this is kiwi', ( 0, 4 ) ),
      ( 'orange.txt', 1, 'this', 'this is orange', ( 0, 4 ) ),
    ]
    self.assertEqual( expected, actual )
    
  def test_search_not_relative(self):
    r = self.data_dir()
    actual = file_search.search(r, 'this', relative = False)
    expected = [
      ( path.join(r, 'apple.txt'), 1, 'this', 'this is apple', ( 0, 4 ) ),
      ( path.join(r, 'kiwi.txt'), 1, 'this', 'this is kiwi', ( 0, 4 ) ),
      ( path.join(r, 'orange.txt'), 1, 'this', 'this is orange', ( 0, 4 ) ),
    ]
    self.assertEqual( expected, actual )
    
if __name__ == '__main__':
  unit_test.main()
