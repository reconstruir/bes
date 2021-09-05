#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.text.text_line_parser import text_line_parser
from bes.text.text_line import text_line as text_line
from bes.text.string_list import string_list

class test_text_line_parser(unit_test):

  def test___init__invalid_text(self):
    with self.assertRaises(TypeError) as ex:
      text_line_parser(None)

    with self.assertRaises(TypeError) as ex:
      text_line_parser(5)
      
  def test___init__empty(self):
    l = text_line_parser('')
    self.assertEqual( 0, len(l) )

  def test___init__with_lines(self):
    l1 = text_line_parser('apple\nkiwi\npear\nmelon')
    self.assertEqual( 4, len(l1) )
    l2 = text_line_parser(l1)
    self.assertEqual( 4, len(l2) )
    self.assertEqual( ( 1, 'apple' ), l2[0] )
    self.assertEqual( ( 2, 'kiwi' ), l2[1] )
    self.assertEqual( ( 3, 'pear' ), l2[2] )
    self.assertEqual( ( 4, 'melon' ), l2[3] )
    
  def test___init__with_text_line_seq(self):
    lines = [ text_line( 1, 'apple' ), text_line( 2, 'kiwi' ), text_line( 3, 'pear' ), text_line( 4, 'melon' ) ]
    l = text_line_parser(lines)
    self.assertEqual( 4, len(l) )
    self.assertEqual( ( 1, 'apple' ), l[0] )
    self.assertEqual( ( 2, 'kiwi' ), l[1] )
    self.assertEqual( ( 3, 'pear' ), l[2] )
    self.assertEqual( ( 4, 'melon' ), l[3] )
    
  def test___init__with_tuple_seq(self):
    lines = [ ( 1, 'apple' ), ( 2, 'kiwi' ), ( 3, 'pear' ), ( 4, 'melon' ) ]
    l = text_line_parser(lines)
    self.assertEqual( 4, len(l) )
    self.assertEqual( ( 1, 'apple' ), l[0] )
    self.assertEqual( ( 2, 'kiwi' ), l[1] )
    self.assertEqual( ( 3, 'pear' ), l[2] )
    self.assertEqual( ( 4, 'melon' ), l[3] )

  def test___init__with_text_line_seq_invalid_line_number(self):
    with self.assertRaises(ValueError) as ex:
      text_line_parser([ text_line( 1, 'apple' ), text_line( 1, 'kiwi' ) ])

  def test___init__with_lines_and_starting_line_number(self):
    l1 = text_line_parser('apple\nkiwi\npear\nmelon', starting_line_number = 5)
    self.assertEqual( 4, len(l1) )
    l2 = text_line_parser(l1)
    self.assertEqual( 4, len(l2) )
    self.assertEqual( ( 5, 'apple' ), l2[0] )
    self.assertEqual( ( 6, 'kiwi' ), l2[1] )
    self.assertEqual( ( 7, 'pear' ), l2[2] )
    self.assertEqual( ( 8, 'melon' ), l2[3] )
      
  def test_1_line(self):
    l = text_line_parser('foo')
    self.assertEqual( 1, len(l) )
    self.assertEqual( 'foo', l[0].text )
    
  def test_1_line_with_newline(self):
    l = text_line_parser('foo\n')
    self.assertEqual( 1, len(l) )
    self.assertEqual( 'foo', l[0].text )
    self.assertMultiLineEqual(
      '''foo
''',
      str(l) )
    
  def test_1_empty_line(self):
    l = text_line_parser('\n')
    self.assertEqual( 1, len(l) )
    self.assertEqual( '', l[0].text )
    self.assertMultiLineEqual(
      '''
''',
      str(l) )
    
  def test_basic(self):
    l = text_line_parser('foo bar\napple kiwi')
    self.assertEqual( 2, len(l) )
    self.assertEqual( 'foo bar', l[0].text )
    self.assertEqual( 'apple kiwi', l[1].text )
    
  def test___setitem__(self):
    l = text_line_parser('foo bar\napple kiwi')
    with self.assertRaises(RuntimeError) as context:
      l[0] = 'foo'

  def test_add_line_numbers(self):
    l = text_line_parser('foo\nbar\n')
    l.add_line_numbers()
    self.assertMultiLineEqual(
      '''1|foo
2|bar
''',
      str(l) )

    l = text_line_parser('foo\nbar')
    l.add_line_numbers()
    self.assertMultiLineEqual(
      '''1|foo
2|bar''',
      str(l) )
    
  def test_prepend(self):
    l = text_line_parser('foo\nbar\n')
    l.prepend('ABC: ')
    self.assertMultiLineEqual(
      '''ABC: foo
ABC: bar
''',
      str(l) )

  def test_prepend_with_index(self):
    l = text_line_parser('1234\n5678')
    l.prepend('_', index = 1)
    self.assertMultiLineEqual(
      '''1_234
5_678''',
      str(l) )

  def test_prepend_with_negative_index(self):
    l = text_line_parser('1234\n5678')
    l.prepend('_', index = -2)
    self.assertMultiLineEqual(
      '''12_34
56_78''',
      str(l) )

    
  def test_append(self):
    l = text_line_parser('foo\nbar\n')
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
    l = text_line_parser(text)
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
    l = text_line_parser(text)
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
    ], text_line_parser(text).to_string_list() )
    
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
    ], text_line_parser(text).to_string_list(strip_comments = True) )

  def test_parse_lines(self):
    self.assertEqual( [ 'foo', 'bar' ], text_line_parser.parse_lines('foo\nbar\n') )
    self.assertEqual( [ 'foo', 'bar' ], text_line_parser.parse_lines('foo\nbar') )
    self.assertEqual( [ 'foo', 'bar' ], text_line_parser.parse_lines('\nfoo\nbar') )
    self.assertEqual( [ 'foo', 'bar' ], text_line_parser.parse_lines('\n foo\nbar') )
    self.assertEqual( [ 'foo', 'bar' ], text_line_parser.parse_lines('\n foo\nbar ') )
    self.assertEqual( [ 'foo', 'bar' ], text_line_parser.parse_lines('\n foo\nbar \n') )
    self.assertEqual( [], text_line_parser.parse_lines('\n\n\n') )
    
  def test_match_first(self):
    text = '''
    Health ID: 8573008129436468
  Test Name                                              Results                               Reference Range               Lab
     CHLORIDE                                                                      101                   98-110 mmol/L
'''
    l = text_line_parser(text)
    patterns = [
      r'^\s*Test\s+Name\s\s+Result\s\s+Flag\s\s+Reference\s+Range\s\s+Lab\s*$',
      r'^\s*Test\s+Name\s\s+Results\s\s+Reference\s+Range\s\s+Lab\s*$',
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
    l = text_line_parser(text)
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
    l = text_line_parser(text)
    l.remove_empties()
    self.assertEqual( [ 'foo', 'bar', 'baz' ], l.to_string_list(strip_text = True) )

  def test_strip(self):
    text = '''
    apple
    kiwi
    orange
    '''
    l = text_line_parser(text)
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
    l = text_line_parser(text)
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
    l = text_line_parser(text)
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
    l = text_line_parser(text)
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
    l = text_line_parser(text)
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
    l = text_line_parser(text)
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
    l = text_line_parser(text)
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
    l = text_line_parser(text)
    l.strip()
    self.assertEqual( [ ( 1, 'apple' ), ( 4, 'apricot' ) ], l.match_all('^a.*$') )
    self.assertEqual( [], l.match_all('^nothere.*$') )
    self.assertEqual( [ ( 1, 'apple' ) ], l.match_all('^app.*$') )

  def test_match_backwards(self):
    l = text_line_parser([ ( 1, 'apple' ), ( 2, 'kiwi' ), ( 3, 'orange' ), ( 4, 'apricot' ), ( 5, 'banana' ), ( 6, 'watermelon' ) ])
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
    l = text_line_parser(text)
    sections = l.cut_sections(r'^section\:.*$', r'^\s*$', include_pattern = True)
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
    l = text_line_parser('01234\n56789\nabcde')
    l.annotate_line('-> ', '   ', 1, index = 0)
    self.assertMultiLineEqual(
      '''-> 01234
   56789
   abcde''',
      str(l) )
    
    l = text_line_parser('01234\n56789\nabcde')
    l.annotate_line('-> ', '   ', 2, index = 0)
    self.assertMultiLineEqual(
      '''   01234
-> 56789
   abcde''',
      str(l) )

    l = text_line_parser('01234\n56789\nabcde')
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

    l = text_line_parser(text)
    l._remove_range(0, 0)
    self.assertMultiLineEqual( '''\
apple
melon
cheese
wine
milk
eggs''', str(l) )

    l = text_line_parser(text)
    l._remove_range(0, 1)
    self.assertMultiLineEqual( '''\
melon
cheese
wine
milk
eggs''', str(l) )

    l = text_line_parser(text)
    l._remove_range(0, 2)
    self.assertMultiLineEqual( '''\
cheese
wine
milk
eggs''', str(l) )
    
    l = text_line_parser(text)
    l._remove_range(0, 1)
    self.assertMultiLineEqual( '''\
melon
cheese
wine
milk
eggs''', str(l) )
    
    
    l = text_line_parser(text)
    l._remove_range(1, 1)
    self.assertMultiLineEqual( '''\
kiwi
melon
cheese
wine
milk
eggs''', str(l) )
    
    l = text_line_parser(text)
    l._remove_range(1, 2)
    self.assertMultiLineEqual( '''\
kiwi
cheese
wine
milk
eggs''', str(l) )
    
    l = text_line_parser(text)
    l._remove_range(6, 6)
    self.assertMultiLineEqual( '''\
kiwi
apple
melon
cheese
wine
milk''', str(l) )

    l = text_line_parser(text)
    l._remove_range(5, 6)
    self.assertMultiLineEqual( '''\
kiwi
apple
melon
cheese
wine''', str(l) )

    l = text_line_parser(text)
    l._remove_range(4, 6)
    self.assertMultiLineEqual( '''\
kiwi
apple
melon
cheese''', str(l) )

    l = text_line_parser(text)
    l._remove_range(4, 5)
    self.assertMultiLineEqual( '''\
kiwi
apple
melon
cheese
eggs''', str(l) )


    l = text_line_parser(text)
    l._remove_range(4, 4)
    self.assertMultiLineEqual( '''\
kiwi
apple
melon
cheese
milk
eggs''', str(l) )

    l = text_line_parser(text)
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
    l = text_line_parser(text)
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
    l = text_line_parser(text)
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
    l = text_line_parser(text)
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
    l = text_line_parser(text)
    l.remove_lines([ 1 ])
    self.assertMultiLineEqual( '''\
2 apple
3 melon
4 eggs
5 wine''', str(l) )
    
    l = text_line_parser(text)
    l.remove_lines([ 2 ])
    self.assertMultiLineEqual( '''\
1 kiwi
3 melon
4 eggs
5 wine''', str(l) )

    l = text_line_parser(text)
    l.remove_lines([  5 ])
    self.assertMultiLineEqual( '''\
1 kiwi
2 apple
3 melon
4 eggs''', str(l) )
    
    l = text_line_parser(text)
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
    l = text_line_parser(text)
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
    l = text_line_parser(text)
    self.assertEqual( [ 1, 2, 3, 4 ], l.line_numbers() )
    l.replace_line_with_lines(2, string_list(['wine', 'pepper']))
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
    l = text_line_parser(text)
    l.replace_line_with_lines(1, string_list(['wine', 'pepper']))
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
    l = text_line_parser(text)
    l.replace_line_with_lines(4, string_list(['wine', 'pepper']))
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
    l = text_line_parser(text)
    self.assertEqual( [ 1, 2, 3, 4 ], l.line_numbers() )
    l.remove_line_number(2)
    self.assertEqual( [ 1, 3, 4 ], l.line_numbers() )
    l.renumber()
    self.assertEqual( [ 1, 2, 3 ], l.line_numbers() )
    
  def test_renumber_empty(self):
    l = text_line_parser('')
    self.assertEqual( [], l.line_numbers() )
    l.renumber()
    self.assertEqual( [], l.line_numbers() )
    
  def test_indeces(self):
    text = '''\
kiwi

apple

melon

cheese'''
    l = text_line_parser(text)
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
    l = text_line_parser(text)
    self.assertEqual( [
      ( 1, 'kiwi' ), 
      ( 2, 'apple' ), 
      ( 3, 'melon' ), 
      ( 4, 'cheese' ), 
    ], l.lines )
    self.assertMultiLineEqual( text, str(l) )
    
  def test_expand_continuations(self):
    text = '''foo\\bar\\baz'''
    l = text_line_parser(text)
    self.assertEqual( [
      ( 1, 'foo\\bar\\baz' ), 
    ], l.lines )
    l.expand_continuations()
    self.assertEqual( [
      ( 1, 'foo' ), 
      ( 2, 'bar' ), 
      ( 3, 'baz' ), 
    ], l.lines )
    
  def test_expand_continuations_with_indent(self):
    text = '''foo\\bar\\baz'''
    l = text_line_parser(text)
    self.assertEqual( [
      ( 1, 'foo\\bar\\baz' ), 
    ], l.lines )
    l.expand_continuations(indent = 2)
    self.assertEqual( [
      ( 1, 'foo' ), 
      ( 2, '  bar' ), 
      ( 3, '  baz' ), 
    ], l.lines )

  def test_re_sub(self):
    text = '''\
cheese = brie;
fruit = kiwi;
wine = barolo;
'''
    l = text_line_parser(text)
    pattern = r'cheese\s+=\s+(.*);'
    l.re_sub(r'cheese\s+=\s+(.*);', 'cheese = fontina;')

    expected = '''\
cheese = fontina;
fruit = kiwi;
wine = barolo;
'''
    self.assertMultiLineEqual( expected, str(l) )
    
  def test_re_findall(self):
    text = '''\
cheese = brie;
fruit = kiwi;
wine = barolo;
cheese = cheddar;
'''
    l = text_line_parser(text)
    pattern = r'cheese\s+=\s+(.*);'
    self.assertEqual( [
      ( 0, ( 1, 'cheese = brie;' ), ['brie'] ),
      ( 3, ( 4, 'cheese = cheddar;' ), ['cheddar'] ),
    ], l.re_findall(r'cheese\s+=\s+(.*);') )
    
if __name__ == '__main__':
  unit_test.main()
