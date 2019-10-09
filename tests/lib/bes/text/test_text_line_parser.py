#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.text.text_line_parser import text_line_parser as LTP
from bes.text.text_line import text_line as LT
from bes.text.string_list import string_list as SL

class test_text_line_parser(unit_test):

  def test___init__invalid_text(self):
    with self.assertRaises(TypeError) as ex:
      LTP(None)

    with self.assertRaises(TypeError) as ex:
      LTP(5)
      
  def test___init__empty(self):
    l = LTP('')
    self.assertEqual( 0, len(l) )

  def test___init__with_lines(self):
    l1 = LTP('apple\nkiwi\npear\nmelon')
    self.assertEqual( 4, len(l1) )
    l2 = LTP(l1)
    self.assertEqual( 4, len(l2) )
    self.assertEqual( ( 1, 'apple' ), l2[0] )
    self.assertEqual( ( 2, 'kiwi' ), l2[1] )
    self.assertEqual( ( 3, 'pear' ), l2[2] )
    self.assertEqual( ( 4, 'melon' ), l2[3] )
    
  def test___init__with_text_line_seq(self):
    lines = [ LT( 1, 'apple' ), LT( 2, 'kiwi' ), LT( 3, 'pear' ), LT( 4, 'melon' ) ]
    l = LTP(lines)
    self.assertEqual( 4, len(l) )
    self.assertEqual( ( 1, 'apple' ), l[0] )
    self.assertEqual( ( 2, 'kiwi' ), l[1] )
    self.assertEqual( ( 3, 'pear' ), l[2] )
    self.assertEqual( ( 4, 'melon' ), l[3] )
    
  def test___init__with_tuple_seq(self):
    lines = [ ( 1, 'apple' ), ( 2, 'kiwi' ), ( 3, 'pear' ), ( 4, 'melon' ) ]
    l = LTP(lines)
    self.assertEqual( 4, len(l) )
    self.assertEqual( ( 1, 'apple' ), l[0] )
    self.assertEqual( ( 2, 'kiwi' ), l[1] )
    self.assertEqual( ( 3, 'pear' ), l[2] )
    self.assertEqual( ( 4, 'melon' ), l[3] )

  def test___init__with_text_line_seq_invalid_line_number(self):
    with self.assertRaises(ValueError) as ex:
      LTP([ LT( 1, 'apple' ), LT( 1, 'kiwi' ) ])

  def test___init__with_lines_and_starting_line_number(self):
    l1 = LTP('apple\nkiwi\npear\nmelon', starting_line_number = 5)
    self.assertEqual( 4, len(l1) )
    l2 = LTP(l1)
    self.assertEqual( 4, len(l2) )
    self.assertEqual( ( 5, 'apple' ), l2[0] )
    self.assertEqual( ( 6, 'kiwi' ), l2[1] )
    self.assertEqual( ( 7, 'pear' ), l2[2] )
    self.assertEqual( ( 8, 'melon' ), l2[3] )
      
  def test_1_line(self):
    l = LTP('foo')
    self.assertEqual( 1, len(l) )
    self.assertEqual( 'foo', l[0].text )
    
  def test_1_line_with_newline(self):
    l = LTP('foo\n')
    self.assertEqual( 1, len(l) )
    self.assertEqual( 'foo', l[0].text )
    self.assertMultiLineEqual(
      '''foo
''',
      str(l) )
    
  def test_1_empty_line(self):
    l = LTP('\n')
    self.assertEqual( 1, len(l) )
    self.assertEqual( '', l[0].text )
    self.assertMultiLineEqual(
      '''
''',
      str(l) )
    
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
''',
      str(l) )

    l = LTP('foo\nbar')
    l.add_line_numbers()
    self.assertMultiLineEqual(
      '''1|foo
2|bar''',
      str(l) )
    
  def test_prepend(self):
    l = LTP('foo\nbar\n')
    l.prepend('ABC: ')
    self.assertMultiLineEqual(
      '''ABC: foo
ABC: bar
''',
      str(l) )

  def test_prepend_with_index(self):
    l = LTP('1234\n5678')
    l.prepend('_', index = 1)
    self.assertMultiLineEqual(
      '''1_234
5_678''',
      str(l) )

  def test_prepend_with_negative_index(self):
    l = LTP('1234\n5678')
    l.prepend('_', index = -2)
    self.assertMultiLineEqual(
      '''12_34
56_78''',
      str(l) )

    
  def test_append(self):
    l = LTP('foo\nbar\n')
    l.append(':ABC')
    self.assertMultiLineEqual(
      '''foo:ABC
bar:ABC
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
    
  def test_match_first(self):
    text = '''
    Health ID: 8573008129436468
  Test Name                                              Results                               Reference Range               Lab
     CHLORIDE                                                                      101                   98-110 mmol/L
'''
    l = LTP(text)
    patterns = [
      '^\s*Test\s+Name\s\s+Result\s\s+Flag\s\s+Reference\s+Range\s\s+Lab\s*$',
      '^\s*Test\s+Name\s\s+Results\s\s+Reference\s+Range\s\s+Lab\s*$',
    ]
    self.assertEqual( 3, l.match_first(patterns).line.line_number )
    
  def test_match_first_with_line_number(self):
    text = '''\
apple1
kiwi
apple2
strawberry
banana
kiwi2
'''
    l = LTP(text)
    self.assertEqual( 1, l.match_first([ '^apple.*$' ]).line.line_number )
    self.assertEqual( 'apple1', l.match_first([ '^apple.*$' ]).line.text )
    self.assertEqual( 3, l.match_first([ '^apple.*$' ], line_number = 2).line.line_number )
    self.assertEqual( 'apple2', l.match_first([ '^apple.*$' ], line_number = 2).line.text )
    
  def test_remove_empties(self):
    text = '''
    foo

    bar


    baz


'''
    l = LTP(text)
    l.remove_empties()
    self.assertEqual( [ 'foo', 'bar', 'baz' ], l.to_string_list(strip_text = True) )

  def test_strip(self):
    text = '''
    apple
    kiwi
    orange
    '''
    l = LTP(text)
    l.strip()
    self.assertEqual( [ '', 'apple', 'kiwi', 'orange', '' ], l.to_string_list() )
    
  def test_cut_lines(self):
    text = '''
    apple
    kiwi
    orange
    apricot
    banana
    watermelon'''
    l = LTP(text)
    l.remove_empties()
    l.strip()
    self.assertEqual( [ 'kiwi', 'orange', 'apricot' ], l.cut_lines('^ap.*$', '^ba.*$').to_string_list() )
    self.assertEqual( [ 'banana', 'watermelon' ], l.cut_lines('^apr.*$', None).to_string_list() )
    self.assertEqual( [ 'apple', 'kiwi' ], l.cut_lines(None, '^or.*$').to_string_list() )

  def test_cut_lines_ends_in_line_break(self):
    text = '''
    apple
    kiwi
    orange
    apricot
    banana
    watermelon
    '''
    l = LTP(text)
    l.remove_empties()
    l.strip()
    self.assertEqual( [ 'kiwi', 'orange', 'apricot' ], l.cut_lines('^ap.*$', '^ba.*$').to_string_list() )
    self.assertEqual( [ 'banana', 'watermelon' ], l.cut_lines('^apr.*$', None).to_string_list() )
    self.assertEqual( [ 'apple', 'kiwi' ], l.cut_lines(None, '^or.*$').to_string_list() )

  def test_cut_lines_include_pattern(self):
    text = '''
    apple
    kiwi
    orange
    apricot
    banana
    watermelon
    '''
    l = LTP(text)
    l.remove_empties()
    l.strip()
    self.assertEqual( [ 'apple', 'kiwi', 'orange', 'apricot', 'banana' ], l.cut_lines('^ap.*$', '^ba.*$', include_pattern = True).to_string_list() )
    self.assertEqual( [ 'apricot', 'banana', 'watermelon' ], l.cut_lines('^apr.*$', None, include_pattern = True).to_string_list() )
    self.assertEqual( [ 'apple', 'kiwi', 'orange' ], l.cut_lines(None, '^or.*$', include_pattern = True).to_string_list() )
    
  def test_find_by_line_number(self):
    text = '''apple
    kiwi
    orange
    apricot
    banana
    watermelon'''
    l = LTP(text)
    l.strip()
    self.assertEqual( 0, l.find_by_line_number(1) )
    self.assertEqual( 3, l.find_by_line_number(4) )
    self.assertEqual( 5, l.find_by_line_number(6) )
    self.assertEqual( -1, l.find_by_line_number(666) )
    
  def test_remove_line_number(self):
    text = '''apple
    kiwi
    orange
    apricot
    banana
    watermelon'''
    l = LTP(text)
    l.strip()
    self.assertEqual( None, l.remove_line_number(666) )
    self.assertEqual( ( 1, 'apple' ), l.remove_line_number(1) )
    self.assertEqual( [ 'kiwi', 'orange', 'apricot', 'banana', 'watermelon' ], l.to_string_list() )
    self.assertEqual( ( 6, 'watermelon' ), l.remove_line_number(6) )
    self.assertEqual( [ 'kiwi', 'orange', 'apricot', 'banana' ], l.to_string_list() )
    self.assertEqual( ( 4, 'apricot' ), l.remove_line_number(4) )
    self.assertEqual( [ 'kiwi', 'orange', 'banana' ], l.to_string_list() )
    
  def test_remove_line_number(self):
    text = '''apple
    kiwi
    orange
    apricot
    banana
    watermelon'''
    l = LTP(text)
    l.strip()
    l.combine_lines(1, 2)
    self.assertEqual( [ 'apple kiwi', 'orange', 'apricot', 'banana', 'watermelon' ], l.to_string_list() )
    l.combine_lines(5, 6)
    self.assertEqual( [ 'apple kiwi', 'orange', 'apricot', 'banana watermelon' ], l.to_string_list() )
    l.combine_lines(3, 4)
    self.assertEqual( [ 'apple kiwi', 'orange apricot', 'banana watermelon' ], l.to_string_list() )
    l.combine_lines(1, 3)
    self.assertEqual( [ 'apple kiwi orange apricot', 'banana watermelon' ], l.to_string_list() )
    l.combine_lines(1, 5)
    self.assertEqual( [ 'apple kiwi orange apricot banana watermelon' ], l.to_string_list() )
    
  def test_match_all(self):
    text = '''apple
    kiwi
    orange
    apricot
    banana
    watermelon'''
    l = LTP(text)
    l.strip()
    self.assertEqual( [ ( 1, 'apple' ), ( 4, 'apricot' ) ], l.match_all('^a.*$') )
    self.assertEqual( [], l.match_all('^nothere.*$') )
    self.assertEqual( [ ( 1, 'apple' ) ], l.match_all('^app.*$') )

  def test_match_backwards(self):
    l = LTP([ ( 1, 'apple' ), ( 2, 'kiwi' ), ( 3, 'orange' ), ( 4, 'apricot' ), ( 5, 'banana' ), ( 6, 'watermelon' ) ])
    self.assertEqual( ( 2, 'kiwi' ), l.match_backwards(5, '^ki.*$').line )

  def test_cut_sections(self):
    text = '''\
section:1
a
b
c

section:2
d
e
f

section:3
g
h
i

'''
    l = LTP(text)
    sections = l.cut_sections('^section\:.*$', '^\s*$', include_pattern = True)
    self.assertEqual( 3, len(sections) )
    self.assertEqual( ( 1, 'section:1' ), sections[0][0] )
    self.assertEqual( ( 2, 'a' ), sections[0][1] )
    self.assertEqual( ( 3, 'b' ), sections[0][2] )
    self.assertEqual( ( 4, 'c' ), sections[0][3] )

    self.assertEqual( ( 6, 'section:2' ), sections[1][0] )
    self.assertEqual( ( 7, 'd' ), sections[1][1] )
    self.assertEqual( ( 8, 'e' ), sections[1][2] )
    self.assertEqual( ( 9, 'f' ), sections[1][3] )

    self.assertEqual( ( 11, 'section:3' ), sections[2][0] )
    self.assertEqual( ( 12, 'g' ), sections[2][1] )
    self.assertEqual( ( 13, 'h' ), sections[2][2] )
    self.assertEqual( ( 14, 'i' ), sections[2][3] )

  def test_annotate_line(self):
    l = LTP('01234\n56789\nabcde')
    l.annotate_line('-> ', '   ', 1, index = 0)
    self.assertMultiLineEqual(
      '''-> 01234
   56789
   abcde''',
      str(l) )
    
    l = LTP('01234\n56789\nabcde')
    l.annotate_line('-> ', '   ', 2, index = 0)
    self.assertMultiLineEqual(
      '''   01234
-> 56789
   abcde''',
      str(l) )

    l = LTP('01234\n56789\nabcde')
    l.annotate_line('-> ', '   ', 3, index = 0)
    self.assertMultiLineEqual(
      '''   01234
   56789
-> abcde''',
      str(l) )
    
  def test__remove_range(self):
    text = '''\
kiwi
apple
melon
cheese
wine
milk
eggs'''

    l = LTP(text)
    l._remove_range(0, 0)
    self.assertMultiLineEqual( '''\
apple
melon
cheese
wine
milk
eggs''', str(l) )

    l = LTP(text)
    l._remove_range(0, 1)
    self.assertMultiLineEqual( '''\
melon
cheese
wine
milk
eggs''', str(l) )

    l = LTP(text)
    l._remove_range(0, 2)
    self.assertMultiLineEqual( '''\
cheese
wine
milk
eggs''', str(l) )
    
    l = LTP(text)
    l._remove_range(0, 1)
    self.assertMultiLineEqual( '''\
melon
cheese
wine
milk
eggs''', str(l) )
    
    
    l = LTP(text)
    l._remove_range(1, 1)
    self.assertMultiLineEqual( '''\
kiwi
melon
cheese
wine
milk
eggs''', str(l) )
    
    l = LTP(text)
    l._remove_range(1, 2)
    self.assertMultiLineEqual( '''\
kiwi
cheese
wine
milk
eggs''', str(l) )
    
    l = LTP(text)
    l._remove_range(6, 6)
    self.assertMultiLineEqual( '''\
kiwi
apple
melon
cheese
wine
milk''', str(l) )

    l = LTP(text)
    l._remove_range(5, 6)
    self.assertMultiLineEqual( '''\
kiwi
apple
melon
cheese
wine''', str(l) )

    l = LTP(text)
    l._remove_range(4, 6)
    self.assertMultiLineEqual( '''\
kiwi
apple
melon
cheese''', str(l) )

    l = LTP(text)
    l._remove_range(4, 5)
    self.assertMultiLineEqual( '''\
kiwi
apple
melon
cheese
eggs''', str(l) )


    l = LTP(text)
    l._remove_range(4, 4)
    self.assertMultiLineEqual( '''\
kiwi
apple
melon
cheese
milk
eggs''', str(l) )

    l = LTP(text)
    l._remove_range(0, 6)
    self.assertMultiLineEqual( '''''', str(l) )

  def test_fold_by_lines(self):
    text = '''\
kiwi
apple
melon
cheese
wine
milk
eggs'''
    l = LTP(text)
    l.fold_by_lines(1, 2, 'cream')
    self.assertMultiLineEqual( '''\
cream
melon
cheese
wine
milk
eggs''', str(l) )

  def test_replace_line_text(self):
    text = '''\
kiwi
apple
melon
eggs'''
    l = LTP(text)
    l.replace_line_text(3, 'whiskey')
    self.assertMultiLineEqual( '''\
kiwi
apple
whiskey
eggs''', str(l) )

  def test_append_line(self):
    text = '''\
kiwi
apple
melon
eggs'''
    l = LTP(text)
    l.append_line('wine')
    self.assertMultiLineEqual( '''\
kiwi
apple
melon
eggs
wine''', str(l) )

  def test_remove_lines(self):
    text = '''\
1 kiwi
2 apple
3 melon
4 eggs
5 wine'''
    l = LTP(text)
    l.remove_lines([ 1 ])
    self.assertMultiLineEqual( '''\
2 apple
3 melon
4 eggs
5 wine''', str(l) )
    
    l = LTP(text)
    l.remove_lines([ 2 ])
    self.assertMultiLineEqual( '''\
1 kiwi
3 melon
4 eggs
5 wine''', str(l) )

    l = LTP(text)
    l.remove_lines([  5 ])
    self.assertMultiLineEqual( '''\
1 kiwi
2 apple
3 melon
4 eggs''', str(l) )
    
    l = LTP(text)
    l.remove_lines([ 1, 3, 5 ])
    self.assertMultiLineEqual( '''\
2 apple
4 eggs''', str(l) )

  def test_add_empty_lines(self):
    text = '''\
kiwi
apple
melon
cheese'''
    l = LTP(text)
    l.add_empty_lines()
    self.assertMultiLineEqual( '''\
kiwi

apple

melon

cheese''', str(l) )

  def test_replace_line_with_lines(self):
    text = '''\
kiwi
apple
melon
cheese'''
    l = LTP(text)
    self.assertEqual( [ 1, 2, 3, 4 ], l.line_numbers() )
    l.replace_line_with_lines(2, SL(['wine', 'pepper']))
    self.assertMultiLineEqual( '''\
kiwi
wine
pepper
melon
cheese''', str(l) )
    self.assertEqual( [ 1, 2, 3, 4, 5 ], l.line_numbers() )
    return
  
    text = '''\
kiwi
apple
melon
cheese'''
    l = LTP(text)
    l.replace_line_with_lines(1, SL(['wine', 'pepper']))
    self.assertMultiLineEqual( '''\
wine
pepper
apple
pepper
melon
cheese''', str(l) )

    text = '''\
kiwi
apple
melon
cheese'''
    l = LTP(text)
    l.replace_line_with_lines(4, SL(['wine', 'pepper']))
    self.assertMultiLineEqual( '''\
kiwi
apple
pepper
melon
wine
pepper''', str(l) )

  def test_renumber(self):
    text = '''\
kiwi
apple
melon
cheese'''
    l = LTP(text)
    self.assertEqual( [ 1, 2, 3, 4 ], l.line_numbers() )
    l.remove_line_number(2)
    self.assertEqual( [ 1, 3, 4 ], l.line_numbers() )
    l.renumber()
    self.assertEqual( [ 1, 2, 3 ], l.line_numbers() )
    
  def test_renumber_empty(self):
    l = LTP('')
    self.assertEqual( [], l.line_numbers() )
    l.renumber()
    self.assertEqual( [], l.line_numbers() )
    
  def test_indeces(self):
    text = '''\
kiwi

apple

melon

cheese'''
    l = LTP(text)
    self.assertEqual( [
      ( 1, 'kiwi' ), 
      ( 2, '' ), 
      ( 3, 'apple' ), 
      ( 4, '' ), 
      ( 5, 'melon' ), 
      ( 6, '' ), 
      ( 7, 'cheese' ), 
    ], l.lines )
    self.assertEqual( { 7: 6, 5: 4, 3: 2 }, l.indeces([ 7, 5, 3 ]) )
    l.remove_empties()
    self.assertEqual( [
      ( 1, 'kiwi' ), 
      ( 3, 'apple' ), 
      ( 5, 'melon' ), 
      ( 7, 'cheese' ), 
    ], l.lines )
    self.assertEqual( { 7: 3, 5: 2, 3: 1 }, l.indeces([ 7, 5, 3 ]) )
    l.renumber()
    self.assertEqual( [
      ( 1, 'kiwi' ), 
      ( 2, 'apple' ), 
      ( 3, 'melon' ), 
      ( 4, 'cheese' ), 
    ], l.lines )
    self.assertEqual( { 3: 2 }, l.indeces([ 7, 5, 3 ]) )

  def test_windows_line_break(self):
    'Test that windows line breaks are interpreted and preserved correctly.'
    text = '''kiwi\r\napple\r\nmelon\r\ncheese\r\n'''
    l = LTP(text)
    self.assertEqual( [
      ( 1, 'kiwi' ), 
      ( 2, 'apple' ), 
      ( 3, 'melon' ), 
      ( 4, 'cheese' ), 
    ], l.lines )
    self.assertMultiLineEqual( text, str(l) )
    
if __name__ == '__main__':
  unit_test.main()
