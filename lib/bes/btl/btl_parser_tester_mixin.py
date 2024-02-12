#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

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
