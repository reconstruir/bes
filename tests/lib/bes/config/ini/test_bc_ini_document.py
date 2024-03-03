#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test

from bes.btl.btl_parser_options import btl_parser_options
from bes.config.ini.bc_ini_document import bc_ini_document

class test_bc_ini_document(unit_test):

  def test_get_section_value(self):
    text = '''
[fruit]
name=apple
color=red

[cheese]
name=vieux
smell=stink
'''
    doc = bc_ini_document(text)
    
    self.assertEqual( 'apple', doc.get_section_value('fruit', 'name') )
    self.assertEqual( 'red', doc.get_section_value('fruit', 'color') )

    self.assertEqual( 'vieux', doc.get_section_value('cheese', 'name') )
    self.assertEqual( 'stink', doc.get_section_value('cheese', 'smell') )

  def test_get_value(self):
    text = '''
name=grocery
version=1.0

[fruit]
name=apple
color=red

[cheese]
name=vieux
smell=stink
'''
    doc = bc_ini_document(text)

    self.assertEqual( 'grocery', doc.get_value('name') )
    self.assertEqual( '1.0', doc.get_value('version') )

  def test_set_value(self):
    text = '''
name=grocery
version=1.0

[fruit]
name=apple
color=red

[cheese]
name=vieux
smell=stink
'''
    doc = bc_ini_document(text)
    self.assert_python_code_text_equal( text, doc.to_source_string() )
    doc.set_value('name', 'restaurant')
    doc.set_value('version', '2.0')
    expected = '''
name=restaurant
version=2.0

[fruit]
name=apple
color=red

[cheese]
name=vieux
smell=stink
'''
    self.assert_python_code_text_equal( expected, doc.to_source_string() )

  def test_add_value(self):
    text = '''
name=restaurant
version=1.0

[fruit]
name=apple
color=red

[cheese]
name=vieux
smell=stink
'''
    doc = bc_ini_document(text)
    self.assert_python_code_text_equal( text, doc.to_source_string() )
    doc.add_value('price', 'expensive')
    doc.add_value('style', 'seafood')
    expected = '''
name=restaurant
version=1.0
price=expensive
style=seafood

[fruit]
name=apple
color=red

[cheese]
name=vieux
smell=stink
'''
    self.assert_python_code_text_equal( expected, doc.text )
    
  def test_set_section_value(self):
    text = '''
[fruit]
name=apple
color=red

[cheese]
name=vieux
smell=stink
'''
    doc = bc_ini_document(text)

    self.assert_python_code_text_equal( text, doc.to_source_string() )

    doc.set_section_value('fruit', 'name', 'lemon')
    doc.set_section_value('fruit', 'color', 'yellow')

    expected = '''
[fruit]
name=lemon
color=yellow

[cheese]
name=vieux
smell=stink
'''
    self.assert_python_code_text_equal( expected, doc.to_source_string() )

  def test_add_section_value_existing_section(self):
    text = '''
[fruit]
name=apple
color=red

[cheese]
name=vieux
'''
    doc = bc_ini_document(text)

    self.assert_python_code_text_equal( text, doc.to_source_string() )

    doc.add_section_value('cheese', 'smell', 'stink')

    self.assert_python_code_text_equal( '''
[fruit]
name=apple
color=red

[cheese]
name=vieux
smell=stink
''', doc.to_source_string() )
    
  def test_remove_section(self):
    text = '''
name=grocery
version=1.0

[fruit]
name=apple
color=red

[cheese]
name=vieux
smell=stink
'''
    doc = bc_ini_document(text)
    self.assert_python_code_text_equal( text, doc.to_source_string() )
    expected = '''
name=grocery
version=1.0

[cheese]
name=vieux
smell=stink
'''
    doc.remove_section('fruit')
    self.assert_python_code_text_equal( expected, doc.to_source_string() )

  def test_remove_empty_section(self):
    text = '''
[fruit]

[cheese]
name=vieux
smell=stink
'''
    doc = bc_ini_document(text)
    self.assert_python_code_text_equal( text, doc.to_source_string() )
    expected = '''
    
[cheese]
name=vieux
smell=stink
'''
    doc.remove_section('fruit')
    self.assert_python_code_text_equal( expected, doc.to_source_string() )

  def test_remove_top_section(self):
    text = '''[fruit]
[cheese]
name=vieux
smell=stink'''
    doc = bc_ini_document(text)
    self.assert_python_code_text_equal( text, doc.to_source_string() )
    expected = '''[cheese]
name=vieux
smell=stink
'''
    doc.remove_section('fruit')
    self.assert_python_code_text_equal( expected, doc.to_source_string() )

  def test_global_add_node_from_text(self):
    text = '''
name=vieux
smell=stink
'''
    doc = bc_ini_document(text)
    self.assert_python_code_text_equal( text, doc.to_source_string() )
    expected = '''
name=vieux
smell=stink
price=cheap
'''
    self.assertMultiLineEqual( '''\
0: t_line_break:[NL]:p=1,1:h=h_line_break:i=0
1: t_key:name:p=2,1:i=1
2: t_key_value_delimiter:=:p=2,5:i=2
3: t_value:vieux:p=2,6:i=3
4: t_line_break:[NL]:p=2,11:h=h_line_break:i=4
5: t_key:smell:p=3,1:i=5
6: t_key_value_delimiter:=:p=3,6:i=6
7: t_value:stink:p=3,7:i=7
8: t_line_break:[NL]:p=3,12:h=h_line_break:i=8
9: t_done::h=h_done:i=9\
''', doc.tokens.to_debug_str() )
    
    doc.add_node_from_text(doc.find_global_section_node(),
                           '\nprice=cheap\n',
                           ( 'n_global_section', 'n_key_value' ))

    self.assertMultiLineEqual( '''\
 0: t_line_break:[NL]:p=1,1:h=h_line_break:i=0
 1: t_key:name:p=2,1:i=1
 2: t_key_value_delimiter:=:p=2,5:i=2
 3: t_value:vieux:p=2,6:i=3
 4: t_line_break:[NL]:p=2,11:h=h_line_break:i=4
 5: t_key:smell:p=3,1:i=5
 6: t_key_value_delimiter:=:p=3,6:i=6
 7: t_value:stink:p=3,7:i=7
 8: t_line_break:[NL]:p=3,12:h=h_line_break:i=8
 9: t_key:price:p=4,1:i=9
10: t_key_value_delimiter:=:p=4,6:i=10
11: t_value:cheap:p=4,7:i=11
12: t_line_break:[NL]:p=4,12:h=h_line_break:i=12
13: t_line_break:[NL]:p=5,1:h=h_line_break:i=13
14: t_done::h=h_done:i=14\
''', doc.tokens.to_debug_str() )
    
    self.assert_python_code_text_equal( expected, doc.to_source_string() )

  def test_section_add_node_from_text(self):
    text = '''
[fruit]
name=kiwi
color=green

[cheese]
name=vieux
smell=stink
'''
    doc = bc_ini_document(text)
    self.assert_python_code_text_equal( text, doc.to_source_string() )
    expected = '''
[fruit]
name=kiwi
color=green
price=cheap


[cheese]
name=vieux
smell=stink
'''
    self.assertMultiLineEqual( '''\
 0: t_line_break:[NL]:p=1,1:h=h_line_break:i=0
 1: t_section_name_begin:[:p=2,1:i=1
 2: t_section_name:fruit:p=2,2:i=2
 3: t_section_name_end:]:p=2,7:i=3
 4: t_line_break:[NL]:p=2,8:h=h_line_break:i=4
 5: t_key:name:p=3,1:i=5
 6: t_key_value_delimiter:=:p=3,5:i=6
 7: t_value:kiwi:p=3,6:i=7
 8: t_line_break:[NL]:p=3,10:h=h_line_break:i=8
 9: t_key:color:p=4,1:i=9
10: t_key_value_delimiter:=:p=4,6:i=10
11: t_value:green:p=4,7:i=11
12: t_line_break:[NL]:p=4,12:h=h_line_break:i=12
13: t_line_break:[NL]:p=5,1:h=h_line_break:i=13
14: t_section_name_begin:[:p=6,1:i=14
15: t_section_name:cheese:p=6,2:i=15
16: t_section_name_end:]:p=6,8:i=16
17: t_line_break:[NL]:p=6,9:h=h_line_break:i=17
18: t_key:name:p=7,1:i=18
19: t_key_value_delimiter:=:p=7,5:i=19
20: t_value:vieux:p=7,6:i=20
21: t_line_break:[NL]:p=7,11:h=h_line_break:i=21
22: t_key:smell:p=8,1:i=22
23: t_key_value_delimiter:=:p=8,6:i=23
24: t_value:stink:p=8,7:i=24
25: t_line_break:[NL]:p=8,12:h=h_line_break:i=25
26: t_done::h=h_done:i=26\
''', doc.tokens.to_debug_str() )
    
    doc.add_node_from_text(doc.find_section_node('fruit'),
                           '\nprice=cheap\n',
                           ( 'n_global_section', 'n_key_value' ))

    self.assertMultiLineEqual( '''\
 0: t_line_break:[NL]:p=1,1:h=h_line_break:i=0
 1: t_section_name_begin:[:p=2,1:i=1
 2: t_section_name:fruit:p=2,2:i=2
 3: t_section_name_end:]:p=2,7:i=3
 4: t_line_break:[NL]:p=2,8:h=h_line_break:i=4
 5: t_key:name:p=3,1:i=5
 6: t_key_value_delimiter:=:p=3,5:i=6
 7: t_value:kiwi:p=3,6:i=7
 8: t_line_break:[NL]:p=3,10:h=h_line_break:i=8
 9: t_key:color:p=4,1:i=9
10: t_key_value_delimiter:=:p=4,6:i=10
11: t_value:green:p=4,7:i=11
12: t_line_break:[NL]:p=4,12:h=h_line_break:i=12
13: t_key:price:p=5,1:i=13
14: t_key_value_delimiter:=:p=5,6:i=14
15: t_value:cheap:p=5,7:i=15
16: t_line_break:[NL]:p=5,12:h=h_line_break:i=16
17: t_line_break:[NL]:p=6,1:h=h_line_break:i=17
18: t_line_break:[NL]:p=7,1:h=h_line_break:i=18
19: t_section_name_begin:[:p=8,1:i=19
20: t_section_name:cheese:p=8,2:i=20
21: t_section_name_end:]:p=8,8:i=21
22: t_line_break:[NL]:p=8,9:h=h_line_break:i=22
23: t_key:name:p=9,1:i=23
24: t_key_value_delimiter:=:p=9,5:i=24
25: t_value:vieux:p=9,6:i=25
26: t_line_break:[NL]:p=9,11:h=h_line_break:i=26
27: t_key:smell:p=10,1:i=27
28: t_key_value_delimiter:=:p=10,6:i=28
29: t_value:stink:p=10,7:i=29
30: t_line_break:[NL]:p=10,12:h=h_line_break:i=30
31: t_done::h=h_done:i=31\
''', doc.tokens.to_debug_str() )
    
    self.assert_python_code_text_equal( expected, doc.to_source_string() )
    
  def test_add_comment_new_line(self):
    text = '''
name=vieux
smell=stink
'''
    doc = bc_ini_document(text)
    self.assert_python_code_text_equal( text, doc.to_source_string() )
    expected = '''
name=vieux
; this is my comment
smell=stink
'''
    doc.add_comment(3, ' this is my comment', 'new_line')
    self.assert_python_code_text_equal( expected, doc.to_source_string() )

  def test_add_comment_end_of_line(self):
    text = '''
name=vieux
smell=stink
'''
    doc = bc_ini_document(text)
    self.assert_python_code_text_equal( text, doc.to_source_string() )
    expected = '''
name=vieux
smell=stink ; this is my comment
'''
    doc.add_comment(3, ' this is my comment', 'end_of_line')
    self.assert_python_code_text_equal( expected, doc.to_source_string() )

  def test_add_comment_start_of_line(self):
    text = '''
name=vieux
smell=stink
'''
    doc = bc_ini_document(text)
    self.assert_python_code_text_equal( text, doc.to_source_string() )
    expected = '''
name=vieux
;smell=stink
'''
    doc.add_comment(3, '', 'start_of_line')
    self.assert_python_code_text_equal( expected, doc.to_source_string() )
    
  def test_add_comment_new_line_with_begin_char(self):
    text = '''
name=vieux
smell=stink
'''
    variables = { 'v_comment_begin': '#' }
    options = btl_parser_options(variables = variables)
    doc = bc_ini_document(text, parser_options = options)
    self.assert_python_code_text_equal( text, doc.to_source_string() )
    expected = '''
name=vieux
# this is my comment
smell=stink
'''
    doc.add_comment(3, ' this is my comment', 'new_line')
    self.assert_python_code_text_equal( expected, doc.to_source_string() )
    
  def test_find_global_section_node(self):
    doc = bc_ini_document('')
    expected = '''
n_global_section;
'''
    self.assert_python_code_text_equal( expected, str(doc.find_global_section_node()) )

  def test_find_sections_node(self):
    text = '''
[fruits]
'''
    doc = bc_ini_document(text)
    expected = '''
n_sections;
  n_section;t_section_name:fruits:p=2,2:i=2    
'''
    self.assert_python_code_text_equal( expected, str(doc.find_sections_node()) )

  def test_empty_text(self):
    doc = bc_ini_document('')
    expected = '''
n_root;
  n_global_section;
  n_sections;
'''
    self.assert_python_code_text_equal( expected, str(doc.root_node) )

  def test_has_section(self):
    text = '''
[fruit]

[cheese]
name=vieux
smell=stink
'''
    doc = bc_ini_document(text)
    self.assertEqual( True, doc.has_section('fruit') )
    self.assertEqual( True, doc.has_section('cheese') )
    self.assertEqual( False, doc.has_section('wine') )
    
  def xxx_test_add_section(self):
    text = '''
[fruit]

[cheese]
name=vieux
smell=stink
'''
    doc = bc_ini_document(text)
    doc.add_section('wine')
    #print(f'NODES BEFORE:{str(doc.root_node)}')
    #doc.tokens.dump(f'TOKENS BEFORE:')
    doc.add_section_value('wine', 'name', 'barolo')
    #print(f'AFTER:{str(doc.root_node)}')
    self.assert_python_code_text_equal( '''
[fruit]

[cheese]
name=vieux
smell=stink

[wine]
name=barolo
''', doc.text )

    self.assert_python_code_text_equal( '''
n_root;
  n_global_section;
  n_sections;
    n_section;t_section_name:fruit:p=2,2:i=2
    n_section;t_section_name:cheese:p=4,2:i=7
      n_key_value;
        n_key;t_key:name:p=5,1:i=10
        n_value;t_value:vieux:p=5,6:i=12
      n_key_value;
        n_key;t_key:smell:p=6,1:i=14
        n_value;t_value:stink:p=6,7:i=16
    n_section;t_section_name:wine:p=8,2:i=20
''', str(doc.root_node) )
    
  def test_add_section_value_at_end(self):
    text = '''
[fruit]

[cheese]
name=vieux
smell=stink

[wine]
'''
    doc = bc_ini_document(text)
    doc.add_section_value('wine', 'name', 'barolo')
    doc.add_section_value('fruit', 'name', 'pear')
    self.assert_python_code_text_equal( '''
[fruit]
name=pear

[cheese]
name=vieux
smell=stink

[wine]
name=barolo
''', doc.text )

    self.assert_python_code_text_equal( '''
n_root;
  n_global_section;
  n_sections;
    n_section;t_section_name:fruit:p=2,2:i=2
      n_key_value;
        n_key;t_key:name:p=3,1:i=5
        n_value;t_value:pear:p=3,6:i=7
    n_section;t_section_name:cheese:p=5,2:i=11
      n_key_value;
        n_key;t_key:name:p=6,1:i=14
        n_value;t_value:vieux:p=6,6:i=16
      n_key_value;
        n_key;t_key:smell:p=7,1:i=18
        n_value;t_value:stink:p=7,7:i=20
    n_section;t_section_name:wine:p=9,2:i=24
      n_key_value;
        n_key;t_key:name:p=10,1:i=27
        n_value;t_value:barolo:p=10,6:i=29    
''', str(doc.root_node) )
    
  def xtest_save_file(self):
    doc = bc_ini_document('')
    expected = '''
n_root;
  n_global_section;
  n_sections;
'''
    self.assert_python_code_text_equal( expected, str(doc.root_node) )
    
if __name__ == '__main__':
  unit_test.main()
