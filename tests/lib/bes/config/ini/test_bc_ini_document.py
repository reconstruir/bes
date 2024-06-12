#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system.host import host
from bes.testing.unit_test import unit_test

from bes.btl.btl_lexer_token import btl_lexer_token
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
    self.assert_python_code_text_equal( text, doc.text )
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
    self.assert_python_code_text_equal( expected, doc.text )

  def test_set_value_simple(self):
    text = '''
name=grocery
'''
    doc = bc_ini_document(text)
    self.assert_python_code_text_equal( text, doc.text )
    doc.set_value('name', 'restaurant')
    expected = '''
name=restaurant
'''
    self.assert_python_code_text_equal( expected, doc.text )
    
  def broken_test_add_value(self):
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
    self.assert_python_code_text_equal( text, doc.text )
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

    self.assert_python_code_text_equal( text, doc.text )

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
    self.assert_python_code_text_equal( expected, doc.text )

  def test_add_section_empty_text(self):
    doc = bc_ini_document('')

    doc.add_section('cheese')

    self.assert_python_code_text_equal( '''
[cheese]
''', doc.text )

    self.assert_python_code_text_equal( '''
n_root;
  n_global_section;
  n_sections;
    n_section;t_section_name:cheese:p=2,2:i=2
''', str(doc.root_node) )

    line_break='[CR][NL]' if host.is_windows() else '[NL]'
    self.assert_python_code_text_equal( f'''
0: t_line_break:{line_break}:p=1,1:h=h_line_break:i=0
1: t_section_name_begin:[:p=2,1:i=1
2: t_section_name:cheese:p=2,2:i=2
3: t_section_name_end:]:p=2,8:i=3
4: t_line_break:{line_break}:p=2,9:h=h_line_break:i=4
''', doc.tokens.to_debug_str() )

  def broken_test_add_section_one_previous_empty_section(self):
    doc = bc_ini_document('[wine]')

    doc.add_section('cheese')

    self.assertMultiLineEqual( '''\
[wine]
[cheese]
''', doc.text )

    self.assert_python_code_text_equal( '''
n_root;
  n_global_section;
  n_sections;
    n_section;t_section_name:wine:p=1,2:i=1
    n_section;t_section_name:cheese:p=2,2:i=5
''', str(doc.root_node) )

    self.assert_python_code_text_equal( '''
0: t_section_name_begin:[:p=1,1:i=0
1: t_section_name:wine:p=1,2:i=1
2: t_section_name_end:]:p=1,6:i=2
3: t_line_break:[NL]:p=1,7:h=h_line_break:i=3
4: t_section_name_begin:[:p=2,1:i=4
5: t_section_name:cheese:p=2,2:i=5
6: t_section_name_end:]:p=2,8:i=6
7: t_line_break:[NL]:p=2,9:h=h_line_break:i=7
''', doc.tokens.to_debug_str() )
    
  def broken_test_add_section_one_previous_non_empty_section(self):
    doc = bc_ini_document('''
[fruit]
name=apple
color=red
''')
    doc.add_section('cheese')
    doc.add_line_break(-1)

    self.assertMultiLineEqual( '''
[fruit]
name=apple
color=red
[cheese]

''', doc.text )

  def broken_test_add_section_value_existing_section(self):
    doc = bc_ini_document('''
[fruit]
name=apple
color=red

[cheese]
name=vieux
''')
    doc.add_section_value('cheese', 'smell', 'stink')
    print('-----')
    print(doc.text.replace(' ', '#'))
    print('-----')
    self.assertMultiLineEqual( '''
[fruit]
name=apple
color=red

[cheese]
name=vieux
smell=stink
''', doc.text )
    
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
    self.assert_python_code_text_equal( text, doc.text )
    expected = '''
name=grocery
version=1.0

[cheese]
name=vieux
smell=stink
'''
    doc.remove_section('fruit')
    self.assert_python_code_text_equal( expected, doc.text )

  def test_remove_empty_section(self):
    text = '''
[fruit]

[cheese]
name=vieux
smell=stink
'''
    doc = bc_ini_document(text)
    self.assert_python_code_text_equal( text, doc.text )
    expected = '''
    
[cheese]
name=vieux
smell=stink
'''
    doc.remove_section('fruit')
    self.assert_python_code_text_equal( expected, doc.text )

  def test_remove_top_section(self):
    text = '''[fruit]
[cheese]
name=vieux
smell=stink'''
    doc = bc_ini_document(text)
    self.assert_python_code_text_equal( text, doc.text )
    expected = '''[cheese]
name=vieux
smell=stink
'''
    doc.remove_section('fruit')
    self.assert_python_code_text_equal( expected, doc.text )

  def test_global_add_node_from_text(self):
    doc = bc_ini_document('''
name=vieux
smell=stink
''')
    parent_node = doc.find_global_section_node()
    doc.add_node_from_text(parent_node,
                           f'price=cheap',
                           ( 'n_global_section', 'n_key_value' ))

    
    self.assertMultiLineEqual( '''
name=vieux
smell=stink
price=cheap
''', doc.text )
    
  def test_section_add_node_from_text_without_line_break(self):
    doc = bc_ini_document('''
[fruit]
name=kiwi
[cheese]
name=vieux
''')
    parent_node = doc.find_section_node('fruit')
    doc.add_node_from_text(parent_node,
                           f'price=cheap',
                           ( 'n_global_section', 'n_key_value' ))

    self.assert_python_code_text_equal( '''
[fruit]
name=kiwi
price=cheap
[cheese]
name=vieux
''', doc.text )
    
  def test_section_add_node_from_text_with_one_line_break(self):
    doc = bc_ini_document('''
[fruit]
name=kiwi

[cheese]
name=vieux
''')
    parent_node = doc.find_section_node('fruit')
    doc.add_node_from_text(parent_node,
                           f'price=cheap',
                           ( 'n_global_section', 'n_key_value' ))

    self.assert_python_code_text_equal( '''
[fruit]
name=kiwi
price=cheap

[cheese]
name=vieux
''', doc.text )

  def test_section_add_node_from_text_with_two_line_breaks(self):
    doc = bc_ini_document('''
[fruit]
name=kiwi


[cheese]
name=vieux
''')
    parent_node = doc.find_section_node('fruit')
    doc.add_node_from_text(parent_node,
                           f'price=cheap',
                           ( 'n_global_section', 'n_key_value' ))

    self.assert_python_code_text_equal( '''
[fruit]
name=kiwi
price=cheap


[cheese]
name=vieux
''', doc.text )

  def test_section_add_node_from_text_with_three_line_breaks(self):
    doc = bc_ini_document('''
[fruit]
name=kiwi



[cheese]
name=vieux
''')
    parent_node = doc.find_section_node('fruit')
    doc.add_node_from_text(parent_node,
                           f'price=cheap',
                           ( 'n_global_section', 'n_key_value' ))

    self.assert_python_code_text_equal( '''
[fruit]
name=kiwi
price=cheap



[cheese]
name=vieux
''', doc.text )
    
  def test_add_comment_new_line(self):
    text = '''
name=vieux
smell=stink
'''
    doc = bc_ini_document(text)
    self.assert_python_code_text_equal( text, doc.text )
    expected = '''
name=vieux
; this is my comment
smell=stink
'''
    doc.add_comment(3, ' this is my comment', 'new_line')
    self.assert_python_code_text_equal( expected, doc.text )
    
  def test_add_comment_new_line(self):
    text = '''
name=vieux
smell=stink
'''
    doc = bc_ini_document(text)
    self.assert_python_code_text_equal( text, doc.text )
    expected = '''
name=vieux
; this is my comment
smell=stink
'''
    doc.add_comment(3, ' this is my comment', 'new_line')
    self.assert_python_code_text_equal( expected, doc.text )
    
  def test_add_comment_end_of_line(self):
    text = '''
name=vieux
smell=stink
'''
    doc = bc_ini_document(text)
    self.assert_python_code_text_equal( text, doc.text )
    expected = '''
name=vieux
smell=stink ; this is my comment
'''
    doc.add_comment(3, ' this is my comment', 'end_of_line')
    self.assert_python_code_text_equal( expected, doc.text )

  def test_add_comment_start_of_line(self):
    text = '''
name=vieux
smell=stink
'''
    doc = bc_ini_document(text)
    self.assert_python_code_text_equal( text, doc.text )
    expected = '''
name=vieux
;smell=stink
'''
    doc.add_comment(3, '', 'start_of_line')
    self.assert_python_code_text_equal( expected, doc.text )
    
  def test_add_comment_new_line_with_begin_char(self):
    text = '''
name=vieux
smell=stink
'''
    variables = { 'v_comment_begin': '#' }
    options = btl_parser_options(variables = variables)
    doc = bc_ini_document(text, parser_options = options)
    self.assert_python_code_text_equal( text, doc.text )
    expected = '''
name=vieux
# this is my comment
smell=stink
'''
    doc.add_comment(3, ' this is my comment', 'new_line')
    self.assert_python_code_text_equal( expected, doc.text )
    
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
    
  def broken_test_add_section_value_at_end(self):
    doc = bc_ini_document('''
[fruit]

[cheese]
name=vieux
smell=stink

[wine]
''')
    doc.add_section_value('wine', 'name', 'barolo')
#    doc.add_section_value('fruit', 'name', 'pear')
    self.assert_python_code_text_equal( '''
[fruit]

[cheese]
name=vieux
smell=stink

[wine]
name=barolo''', doc.text )
    return
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
    
  def broken_test_add_line_break_with_section(self):
    doc = bc_ini_document('''
[fruit]
name=apple
''')
    line = doc.add_section_value('fruit', 'color', 'red')
    doc.add_line_break(line + 1, count = 10)
    doc.add_section('cheese')
    self.assert_python_code_text_equal( '''
[fruit]
name=apple
color=red

[cheese]
''', doc.text )

if __name__ == '__main__':
  unit_test.main()
