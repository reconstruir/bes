#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

from ..text.tree_text_parser import tree_text_parser

from .btl_parser_node import btl_parser_node
from .btl_lexer_token import btl_lexer_token

class btl_parser_tester_mixin:

  _test_result = namedtuple('_test_result', 'expected, actual, expected_source_string, actual_source_string, expected_tokens, actual_tokens')
  def call_lex_all(self, parser_class, text, expected):
    parser = parser_class()
    actual_tokens = parser.parse(text)
    actual_json = actual_tokens.to_json()
    expected_tokens = btl_parser_node_deque(expected)
    expected_json = btl_parser_node_deque(expected).to_json()

    expected_string = '\n'.join([ token.to_debug_str() for token in expected_tokens ])
    actual_string = '\n'.join([ token.to_debug_str() for token in actual_tokens ])

    if self.DEBUG:
      for i, token in enumerate(actual_tokens, start = 1):
        ts = token.to_debug_str()
        print(f'{i}: {ts}', flush = True)

    return self._test_result(expected_string,
                             actual_string,
                             text,
                             actual_tokens.to_source_string(),
                             expected_tokens,
                             actual_tokens)

  @classmethod
  def parse_test_tree(clazz, text):
    tree = tree_text_parser.parse(text,
                                  strip_comments = True,
                                  root_name = 'root')
    btl_tree = clazz._clone_as_btl_parser_node(tree)
    return btl_tree.children[0]

  @classmethod
  def _clone_as_btl_parser_node(clazz, root):
    if root is None:
      return None
    node_name, delimiter, token_str = root.data.text.partition(';')
    token = btl_lexer_token.parse_str(token_str)
    cloned_root = btl_parser_node(node_name, token = token)
    for child in root.children:
       cloned_child = clazz._clone_as_btl_parser_node(child)
       cloned_root.children.append(cloned_child)
    return cloned_root
