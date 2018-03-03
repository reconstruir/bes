#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.text import text_line_parser as LTP

class test_text_line_parser(unit_test):

  def test_empty(self):
    l = LTP('')
    self.assertEqual( 1, len(l) )

  def test_1_line(self):
    l = LTP('foo')
    self.assertEqual( 1, len(l) )
    self.assertEqual( 'foo', l[0].text )
    
  def test_1_line_with_newline(self):
    l = LTP('foo\n')
    self.assertEqual( 2, len(l) )
    self.assertEqual( 'foo', l[0].text )
    self.assertEqual( '', l[1].text )
    
  def test_1_empty_line(self):
    l = LTP('\n')
    self.assertEqual( 2, len(l) )
    self.assertEqual( '', l[0].text )
    self.assertEqual( '', l[1].text )
    
  def test_basic(self):
    l = LTP('foo bar\napple kiwi')
    self.assertEqual( 2, len(l) )
    self.assertEqual( 'foo bar', l[0].text )
    self.assertEqual( 'apple kiwi', l[1].text )
    
  def test___setitem__(self):
    l = LTP('foo bar\napple kiwi')
    with self.assertRaises(RuntimeError) as context:
      l[0] = 'foo'

  def test_add_line_numbers(self):
    l = LTP('foo\nbar\n')
    l.add_line_numbers()
    self.assertMultiLineEqual(
      '''1|foo
2|bar
3|
''',
      str(l) )

  def test_prepend(self):
    l = LTP('foo\nbar\n')
    l.prepend('ABC: ')
    self.assertMultiLineEqual(
      '''ABC: foo
ABC: bar
ABC:
''',
      str(l) )

  def test_append(self):
    l = LTP('foo\nbar\n')
    l.append(':ABC')
    self.assertMultiLineEqual(
      '''foo:ABC
bar:ABC
:ABC
''',
      str(l) )

  def test_continuation(self):
    text = r'''foo bar
kiwi \
apple
pear \
orange
almond \
peanut \
walnut \
rum
coke'''
    l = LTP(text)
    l.merge_continuations()
    l.add_line_numbers()
    self.assertMultiLineEqual(
      ''' 1|foo bar
 2|kiwi apple
 3|
 4|pear orange
 5|
 6|almond peanut walnut rum
 7|
 8|
 9|
10|coke''',
      str(l) )

  def test_strip_comments(self):
    text = r'''foo bar # comment
kiwi # comment
apple
pear # comment
orange
almond # comment
peanut # comment
walnut # comment
rum
coke'''
    l = LTP(text)
    self.assertMultiLineEqual(
      '''foo bar
kiwi
apple
pear
orange
almond
peanut
walnut
rum
coke''',
      l.to_string(strip_comments = True) )

  def test_to_string_list(self):
    text = r'''foo bar # comment
kiwi # comment
apple
pear # comment
orange
almond # comment
peanut # comment
walnut # comment
rum
coke'''
    self.assertEqual( [
      'foo bar # comment',
      'kiwi # comment',
      'apple',
      'pear # comment',
      'orange',
      'almond # comment',
      'peanut # comment',
      'walnut # comment',
      'rum',
      'coke'
    ], LTP(text).to_string_list() )
    
  def test_to_string_list_strip_comments(self):
    text = r'''foo bar # comment
kiwi # comment
apple
pear # comment
orange
almond # comment
peanut # comment
walnut # comment
rum
coke'''
    self.assertEqual( [
      'foo bar',
      'kiwi',
      'apple',
      'pear',
      'orange',
      'almond',
      'peanut',
      'walnut',
      'rum',
      'coke'
    ], LTP(text).to_string_list(strip_comments = True) )

  def test_parse_lines(self):
    self.assertEqual( [ 'foo', 'bar' ], LTP.parse_lines('foo\nbar\n') )
    self.assertEqual( [ 'foo', 'bar' ], LTP.parse_lines('foo\nbar') )
    self.assertEqual( [ 'foo', 'bar' ], LTP.parse_lines('\nfoo\nbar') )
    self.assertEqual( [ 'foo', 'bar' ], LTP.parse_lines('\n foo\nbar') )
    self.assertEqual( [ 'foo', 'bar' ], LTP.parse_lines('\n foo\nbar ') )
    self.assertEqual( [ 'foo', 'bar' ], LTP.parse_lines('\n foo\nbar \n') )
    self.assertEqual( [], LTP.parse_lines('\n\n\n') )
    
  def find_line_with_re(self):
    self.assertEqual( [ 'foo', 'bar' ], LTP.parse_lines('foo\nbar\n') )
    self.assertEqual( [ 'foo', 'bar' ], LTP.parse_lines('foo\nbar') )
    self.assertEqual( [ 'foo', 'bar' ], LTP.parse_lines('\nfoo\nbar') )
    self.assertEqual( [ 'foo', 'bar' ], LTP.parse_lines('\n foo\nbar') )
    self.assertEqual( [ 'foo', 'bar' ], LTP.parse_lines('\n foo\nbar ') )
    self.assertEqual( [ 'foo', 'bar' ], LTP.parse_lines('\n foo\nbar \n') )
    self.assertEqual( [], LTP.parse_lines('\n\n\n') )
    
if __name__ == '__main__':
  unit_test.main()
