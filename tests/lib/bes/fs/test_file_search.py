#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.testing.unit_test import unit_test
from bes.fs.file_search import file_search
from bes.fs.testing.temp_content import temp_content

class test_file_search(unit_test):

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
    tmp_dir = self._make_test_content()
    actual = file_search.search(tmp_dir, 'this', relative = True)
    expected = [
      ( 'apple.txt', 1, 'this', 'this is apple', ( 0, 4 ) ),
      ( 'kiwi.txt', 1, 'this', 'this is kiwi', ( 0, 4 ) ),
      ( 'orange.txt', 1, 'this', 'this is orange', ( 0, 4 ) ),
    ]
    self.assertEqual( expected, actual )
    
  def test_search_not_relative(self):
    tmp_dir = self._make_test_content()
    actual = file_search.search(tmp_dir, 'this', relative = False)
    expected = [
      ( path.join(tmp_dir, 'apple.txt'), 1, 'this', 'this is apple', ( 0, 4 ) ),
      ( path.join(tmp_dir, 'kiwi.txt'), 1, 'this', 'this is kiwi', ( 0, 4 ) ),
      ( path.join(tmp_dir, 'orange.txt'), 1, 'this', 'this is orange', ( 0, 4 ) ),
    ]
    self.assertEqual( expected, actual )

  def _make_test_content(self):
    tmp_dir = temp_content.write_items_to_temp_dir([
        'file apple.txt "this is apple" 644',
        'file kiwi.txt "this is kiwi" 644',
        'file orange.txt "this is orange" 644',
    ])
    return tmp_dir
    
if __name__ == '__main__':
  unit_test.main()
