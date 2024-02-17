#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path

from bes.property.cached_class_property import cached_class_property
from bes.fs.file_util import file_util
from bes.text.tree_text_parser import tree_text_parser
from bes.btl.btl_code_gen_buffer import btl_code_gen_buffer
from bes.btl.btl_desc_text_node import btl_desc_text_node

class _test_simple_parser_mixin:

  @cached_class_property
  def _simple_parser_desc_filename(clazz):
    here = path.dirname(__file__)
    filename = path.join(here, '_test_simple_parser.btp')
    return path.abspath(filename)
  
  @cached_class_property
  def _simple_parser_desc_text(clazz):
    return file_util.read(clazz._simple_parser_desc_filename, codec = 'utf-8')

  @classmethod
  def _simple_parser_desc_tree(clazz):
    return tree_text_parser.parse(clazz._simple_parser_desc_text,
                                  strip_comments = True,
                                  root_name = 'btl_parser_desc',
                                  node_class = btl_desc_text_node)

  @classmethod
  def _simple_parser_desc_tree_section(clazz, section_name):
    root = clazz._simple_parser_desc_tree()
    for child in root.children:
      if child.data.text == section_name:
        return child
    return None

  @classmethod
  def call_function_with_buf(clazz, o, func_name, *args, **kwargs):
    buf = btl_code_gen_buffer()
    func = getattr(o, func_name)
    func(buf, *args, **kwargs)
    return buf.get_value()
