#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

from ..system.check import check
from ..version.semantic_version import semantic_version
from ..fs.file_check import file_check
from ..fs.file_util import file_util
from ..text.tree_text_parser import tree_text_parser

from .btl_desc_header import btl_desc_header
from .btl_desc_error_list import btl_desc_error_list
from .btl_desc_char_list import btl_desc_char_list
from .btl_desc_char_map import btl_desc_char_map

class btl_desc(namedtuple('btl_desc', 'header, tokens, errors, chars, states')):
  
  def __new__(clazz, header, tokens, errors, chars, states):
    header = check.check_btl_desc_header(header)
    check.check_string_seq(tokens)
    errors = check.btl_desc_error_list(errors)
    chars = check.btl_desc_char_list(chars)
    return clazz.__bases__[0].__new__(clazz, header, tokens, errors, chars, states)

  @classmethod
  def parse_text(clazz, text, source = '<unknown>'):
    check.check_string(text)
    check.check_string(source)

    root = tree_text_parser.parse(text, strip_comments = True, root_name = 'btl_desc')
    print(root)
    return None

  @classmethod
  def parse_file(clazz, filename):
    filename = file_check.check_file(filename)
    text = file_util.read(filename, codec = 'utf-8')
    return clazz.parse_text(text, source = filename)
    
    
check.register_class(btl_desc)
