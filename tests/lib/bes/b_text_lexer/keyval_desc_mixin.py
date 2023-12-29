#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path

from bes.property.cached_property import cached_property
from bes.fs.file_util import file_util
from bes.text.tree_text_parser import tree_text_parser
from bes.b_text_lexer.btl_code_gen_buffer import btl_code_gen_buffer

class keyval_desc_mixin:

  def assert_code_equal(self, expected, actual):
    return self.assert_string_equal(expected, actual,
                                    strip = True,
                                    multi_line = True,
                                    ignore_white_space = False,
                                    native_line_breaks = True)
  
  @cached_property
  def _keyval_desc_filename(self):
    here = path.dirname(__file__)
    filename = path.join(here, 'keyval.btl')
    return path.abspath(filename)
  
  @cached_property
  def _keyval_desc_text(self):
    return file_util.read(self._keyval_desc_filename, codec = 'utf-8')

  def _keyval_desc_tree(self):
    return tree_text_parser.parse(self._keyval_desc_text,
                                  strip_comments = True,
                                  root_name = 'btl_desc')

  def _keyval_desc_tree_section(self, section_name):
    root = self._keyval_desc_tree()
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
  
if __name__ == '__main__':
  unit_test.main()