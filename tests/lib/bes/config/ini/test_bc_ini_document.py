#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test

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

  def xtest_global_add_node_from_text(self):
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
    doc.add_node_from_text(doc.find_global_section_node(), 'price=cheap')
    self.assert_python_code_text_equal( expected, doc.to_source_string() )

  def test_caca(self):
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
name=vieux
smell=stink
price=cheap
'''
    last_node = doc.find_global_section_node().find_last_node()
    print(f'last_node={last_node}')
    #doc.add_node_from_text(doc.find_global_section_node, 'price=cheap')
#    self.assert_python_code_text_equal( expected, doc.to_source_string() )

#find_section_node

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
    
if __name__ == '__main__':
  unit_test.main()
