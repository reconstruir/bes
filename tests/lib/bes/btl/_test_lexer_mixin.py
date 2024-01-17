#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

from bes.btl.btl_lexer_token_deque import btl_lexer_token_deque

class _test_lexer_mixin:

  _test_result = namedtuple('_test_result', 'expected, actual, expected_source_string, actual_source_string, expected_tokens, actual_tokens')
  def _test_tokenize(self, lexer_class, text, expected):
    lexer = lexer_class()
    actual_tokens = lexer.tokenize(text)
    actual_json = actual_tokens.to_json()
    expected_tokens = btl_lexer_token_deque(expected)
    expected_json = btl_lexer_token_deque(expected).to_json()

    expected_string = '\n'.join([ str(token) for token in expected_tokens ])
    actual_string = '\n'.join([ str(token) for token in actual_tokens ])

    if self.DEBUG:
      for i, token in enumerate(actual_tokens, start = 1):
        print(f'{i}: {token}', flush = True)

    return self._test_result(expected_string,
                             actual_string,
                             text,
                             actual_tokens.to_source_string(),
                             expected_tokens,
                             actual_tokens)
