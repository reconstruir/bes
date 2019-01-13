#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.text import comments

class test_comments(unit_test):

  def test_strip_line(self):
    self.assertEqual( 'foo ', comments.strip_line('foo #comment', ) )
    self.assertEqual( 'foo', comments.strip_line('foo#comment') )
    self.assertEqual( 'foo', comments.strip_line('foo #comment', strip_tail = True) )
    self.assertEqual( ' foo', comments.strip_line(' foo #comment', strip_tail = True) )
    self.assertEqual( 'foo ', comments.strip_line(' foo #comment', strip_head = True) )
    
  def test_strip_line_allow_quoted(self):
    self.assertEqual( 'ab "cd # ef"', comments.strip_line('ab "cd # ef"', allow_quoted = True) )
    self.assertEqual( 'ab "cd # ef"', comments.strip_line('ab "cd # ef"#comment', allow_quoted = True) )
    self.assertEqual( '', comments.strip_line('#ab "cd # ef"', allow_quoted = True) )
    self.assertEqual( '"#"', comments.strip_line('"#"', allow_quoted = True) )
    
  def test_strip_line_disallow_quoted(self):
    self.assertEqual( 'ab "cd ', comments.strip_line('ab "cd # ef"', allow_quoted = False) )
    self.assertEqual( 'ab "cd ', comments.strip_line('ab "cd # ef"#comment', allow_quoted = False) )
    self.assertEqual( '', comments.strip_line('#ab "cd # ef"', allow_quoted = False) )
    self.assertEqual( '"', comments.strip_line('"#"', allow_quoted = False) )
    
  def test_strip_line_disallow_quoted_escaped(self):
    self.assertEqual( 'ab "cd # ef"', comments.strip_line('ab "cd \# ef"', allow_quoted = False) )
    self.assertEqual( 'ab "cd # ef"', comments.strip_line('ab "cd \# ef"#comment', allow_quoted = False) )
    self.assertEqual( '', comments.strip_line('#ab "cd # ef"', allow_quoted = False) )
    self.assertEqual( '"#"', comments.strip_line('"\#"', allow_quoted = False) )
    
  def test_strip_line_with_strip(self):
    self.assertEqual( 'foo', comments.strip_line('foo #comment', strip_tail = True) )

  def test_strip_strip_in_lines(self):
    text = '''
foo_# comment
# comment
bar
'''
    expected = '''
foo_

bar
'''
    self.assertMultiLineEqual( expected, comments.strip_in_lines(text) )

  def test_strip_strip_in_lines_with_strip(self):
    text = '''
foo # comment
# comment
bar
'''
    expected = '''
foo

bar
'''
    self.assertMultiLineEqual( expected, comments.strip_in_lines(text, strip_tail = True) )

  def test_strip_strip_in_lines_remove_empties(self):
    text = '''
foo_# comment
# comment
bar
'''
    expected = '''foo_
bar'''
    self.assertMultiLineEqual( expected, comments.strip_in_lines(text, remove_empties = True) )
    
  def test_strip_muti_line_comment(self):
    text = '''foo
bar
baz##[apple 
kiwi
melon
lemon
]##peach
orange
'''
    expected = '''foo
bar
bazpeach
orange
'''
    self.assertMultiLineEqual( expected, comments.strip_muti_line_comment(text, '##[', ']##') )
    
  def test_strip_muti_line_replace(self):
    text = '''foo
bar
baz##[apple 
kiwi
melon
lemon
]##peach
orange
'''
    expected = '''foo
bar
baz         
    
     
     
   peach
orange
'''
    self.assertMultiLineEqual( expected, comments.strip_muti_line_comment(text, '##[', ']##', replace = True) )

  def test_strip_muti_line_comment_multiple_comments(self):
    text = '''foo
bar
baz##[apple 
kiwi
melon
lemon
]##peach
orange
cheese
##[burger
bacon
salad
wine
]##
hot dog
fries
'''
    expected = '''foo
bar
bazpeach
orange
cheese

hot dog
fries
'''
    actual = comments.strip_muti_line_comment(text, '##[', ']##')
    self.assertMultiLineEqual( expected, actual )

  def test_strip_muti_line_comment_replace_multiple_comments(self):
    text = '''foo
bar
baz##[apple 
kiwi
melon
lemon
]##peach
orange
cheese
##[burger
bacon
salad
wine
]##
hot dog
fries
'''
    expected = '''foo
bar
baz         
    
     
     
   peach
orange
cheese
         
     
     
    
   
hot dog
fries
'''
    actual = comments.strip_muti_line_comment(text, '##[', ']##', replace = True)
    self.assertMultiLineEqual( expected, actual )
    self.assertEqual( expected.count('\n'), actual.count('\n') )

  def test_strip_muti_line_comment_commented_out(self):
    text = '''foo
bar
baz
###[apple 
kiwi
melon
lemon
#]##
peach
orange
'''
    expected = text
    self.assertMultiLineEqual( expected, comments.strip_muti_line_comment(text, '##[', ']##') )
    
if __name__ == '__main__':
  unit_test.main()
