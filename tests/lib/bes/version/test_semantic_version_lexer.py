#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.text.lexer_token import lexer_token
from bes.common.point import point

from bes.version.semantic_version_lexer import semantic_version_lexer
from bes.version.semantic_version_error import semantic_version_error

def TDONE(x = 0, y = 0): return lexer_token(semantic_version_lexer.TOKEN_DONE, None, point(x, y))
def TTEXT(value, x = 0, y = 0): return lexer_token(semantic_version_lexer.TOKEN_TEXT, value, point(x, y))
def TPUN(value, x = 0, y = 0): return lexer_token(semantic_version_lexer.TOKEN_PUNCTUATION, value, point(x, y))
def TPART(value, x = 0, y = 0): return lexer_token(semantic_version_lexer.TOKEN_PART, value, point(x, y))
def TPD(value, x = 0, y = 0): return lexer_token(semantic_version_lexer.TOKEN_PART_DELIMITER, value, point(x, y))

class test_semantic_version_lexer(unit_test):

  def test_empty_string(self):
    self.assertEqual( [ TDONE(0) ],
                      self._tokenize(r'') )

  def test_text_1_char(self):
    self.assertEqual( [ TTEXT('a', 0), TDONE(1) ],
                      self._tokenize(r'a') )

  def test_text_2_char(self):
    self.assertEqual( [ TTEXT('ab', 0), TDONE(2) ],
                      self._tokenize(r'ab') )

  def test_text_3_chars(self):
    self.assertEqual( [ TTEXT('abc', 0), TDONE(3) ],
                      self._tokenize(r'abc') )

  def test_single_part(self):
    self.assertEqual( [ TPART(1, 0), TDONE(1) ],
                      self._tokenize(r'1') )

  def test_dual_part(self):
    self.assertEqual( [ TPART(12, 0), TDONE(2) ],
                      self._tokenize(r'12') )
    
  def test_single_pun(self):
    self.assertEqual( [ TPUN('!', 0), TDONE(1) ],
                      self._tokenize(r'!') )

  def test_dual_pun(self):
    self.assertEqual( [ TPUN('!!', 0), TDONE(2) ],
                      self._tokenize(r'!!') )

  def test_pd_is_first_char(self):
    with self.assertRaises(semantic_version_error) as ctx:
      self._tokenize(r'.')

  def test_pd_duplicate(self):
    with self.assertRaises(semantic_version_error) as ctx:
      self._tokenize(r'1..2')

  def test_pd_is_last_char(self):
    with self.assertRaises(semantic_version_error) as ctx:
      self._tokenize(r'1.')

  def test_pd_error_after_text(self):
    with self.assertRaises(semantic_version_error) as ctx:
      self._tokenize(r'a.')
      
  def test_pd_1_part(self):
    self.assertEqual( [ TPART(1, 0), TPD('.', 1), TPART(2, 2), TDONE(3) ],
                      self._tokenize(r'1.2') )

  def test_pd_2_parts(self):
    self.assertEqual( [ TPART(1, 0), TPD('.', 1), TPART(2, 2), TPD('.', 3), TPART(3, 4), TDONE(5) ],
                      self._tokenize(r'1.2.3') )

  def test_pd_3_parts(self):
    self.assertEqual( [ TPART(1, 0), TPD('.', 1), TPART(2, 2), TPD('.', 3), TPART(3, 4), TPD('-', 5), TPART(4, 6), TDONE(7) ],
                      self._tokenize(r'1.2.3-4') )
    
  def test_part_and_text(self):
    self.assertEqual( [ TPART(1, 0), TTEXT('a', 1), TDONE(2) ],
                      self._tokenize(r'1a') )
    
  def test_text_and_part(self):
    self.assertEqual( [ TTEXT('a', 0), TPART(1, 1), TDONE(2) ],
                      self._tokenize(r'a1') )
    
  def test_text_pun_and_part(self):
    self.assertEqual( [ TPART(1, 0), TPUN('!', 1), TTEXT('a', 2), TDONE(3) ],
                      self._tokenize(r'1!a') )
    
  def test_build_version_with_alpha(self):
    self.assertEqual( [ TPART(1, 0), TPD('.', 1), TPART(2, 2), TPD('.', 3), TPART(3, 4), TTEXT('a', 5), TDONE(6) ],
                      self._tokenize(r'1.2.3a') )
    
  @classmethod
  def _tokenize(self, text):
    return [ token for token in semantic_version_lexer.tokenize(text, 'unit_test') ]

  def assertEqual(self, expected, actual):
    assert isinstance(expected, list)
    expected = [ lexer_token(*t) for t in expected ]
    super(test_semantic_version_lexer, self).assertEqual(expected, actual)

if __name__ == '__main__':
  unit_test.main()
