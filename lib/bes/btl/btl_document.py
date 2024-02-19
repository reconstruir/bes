#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

from ..system.log import log
from ..system.check import check

from .btl_lexer_token_deque import btl_lexer_token_deque
from .btl_lexer_token_lines import btl_lexer_token_lines
from .btl_parser_desc import btl_parser_desc
from .btl_parser_error import btl_parser_error
from .btl_parser_node import btl_parser_node
from .btl_parser_options import btl_parser_options

class btl_document(object):

  def __init__(self, lexer, parser, text, source = None):
    check.check_btl_lexer(lexer)
    check.check_btl_parser(parser)
    check.check_string(text)
    check.check_string(source, allow_none = True)

    source = source or '<unknown>'
    self._lexer = lexer
    self._parser = parser
    self._root = None
    self._tokens = None

#  @classmethod
#  def from_text(clazz, text):
#    check.check_string(text)

check.register_class(btl_document, include_seq = False)
