#!/usr/bin/env python
#-*- coding:utf-8 -*-
#
import unittest
from bes.fs import file_search

class test_file_search(unittest.TestCase):

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
    
if __name__ == "__main__":
  unittest.main()
