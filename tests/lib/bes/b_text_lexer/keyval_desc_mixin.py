#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path

from bes.property.cached_class_property import cached_class_property
from bes.fs.file_util import file_util
from bes.text.tree_text_parser import tree_text_parser
from bes.b_text_lexer.btl_code_gen_buffer import btl_code_gen_buffer
from bes.text.text_replace import text_replace

class keyval_desc_mixin:

  def assert_code_equal(self, expected, actual, replacements = {}):
    expected2 = text_replace.replace(expected, replacements)
    actual2 = text_replace.replace(actual, replacements)
    return self.assert_string_equal(expected2, actual2,
                                    strip = True,
                                    multi_line = True,
                                    ignore_white_space = False,
                                    native_line_breaks = True)
  
  @cached_class_property
  def _keyval1_desc_filename(clazz):
    here = path.dirname(__file__)
    filename = path.join(here, '_test_keyval1_lexer.btl')
    return path.abspath(filename)
  
  @cached_class_property
  def _keyval1_desc_text(clazz):
    return file_util.read(clazz._keyval1_desc_filename, codec = 'utf-8')

  @classmethod
  def _keyval1_desc_tree(clazz):
    return tree_text_parser.parse(clazz._keyval1_desc_text,
                                  strip_comments = True,
                                  root_name = 'btl_desc')

  @classmethod
  def _keyval1_desc_tree_section(clazz, section_name):
    root = clazz._keyval1_desc_tree()
    for child in root.children:
      if child.data.text == section_name:
        return child
    return None

  @classmethod
  def call_buf_func(clazz, o, func_name, *args, **kwargs):
    buf = btl_code_gen_buffer()
    func = getattr(o, func_name)
    func(buf, *args, **kwargs)
    return buf.get_value()
