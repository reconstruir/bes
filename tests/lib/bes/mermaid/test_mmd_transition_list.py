#!/usr/bin/env python3
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.mermaid.mermaid import mermaid

from example_mmd import INI_MMD

class test_mmd_transition_list(unit_test):

  def test_state_diagram_parse_text(self):
    expected = '''
{
  "__start": {
    "start": []
  }, 
  "start": {
    "end": [
      "EOS"
    ], 
    "comment": [
      "SEMICOLON"
    ], 
    "space": [
      "TAB SPACE"
    ], 
    "cr": [
      "CR"
    ], 
    "start": [
      "NL"
    ], 
    "section_name": [
      "OPEN_BRACKET"
    ], 
    "key": [
      "UNDERSCORE LOWER_LETTER UPPER_LETTER DIGIT"
    ], 
    "expecting_value": [
      "EQUAL"
    ], 
    "start_error": [
      "ANY"
    ]
  }, 
  "space": {
    "space": [
      "TAB SPACE"
    ], 
    "end": [
      "EOS"
    ], 
    "cr": [
      "CR"
    ], 
    "start": [
      "NL"
    ], 
    "key": [
      "UNDERSCORE LOWER_LETTER UPPER_LETTER DIGIT"
    ], 
    "expecting_value": [
      "EQUAL"
    ]
  }, 
  "cr": {
    "start": [
      "NL]"
    ], 
    "cr_error": [
      "ANY EOS"
    ]
  }, 
  "comment": {
    "comment": [
      "ANY"
    ], 
    "cr": [
      "CR"
    ], 
    "start": [
      "NL"
    ], 
    "end": [
      "EOS"
    ]
  }, 
  "section_name": {
    "section_name": [
      "UNDERSCORE LOWER_LETTER UPPER_LETTER DIGIT PERIOD"
    ], 
    "start": [
      "]"
    ], 
    "section_name_error": [
      "TAB SPACE CR NL EOS"
    ]
  }, 
  "key": {
    "key": [
      "UNDERSCORE LOWER_LETTER UPPER_LETTER DIGIT PERIOD"
    ], 
    "space": [
      "TAB SPACE"
    ], 
    "cr": [
      "CR"
    ], 
    "start": [
      "NL"
    ], 
    "expecting_value": [
      "EQUAL"
    ], 
    "end": [
      "EOS"
    ]
  }, 
  "expecting_value": {
    "value_space": [
      "TAB SPACE"
    ], 
    "cr": [
      "CR"
    ], 
    "start": [
      "NL"
    ], 
    "end": [
      "EOS"
    ], 
    "value": [
      "ANY"
    ]
  }, 
  "value_space": {
    "value_space": [
      "TAB SPACE"
    ], 
    "cr": [
      "CR"
    ], 
    "start": [
      "NL"
    ], 
    "end": [
      "EOS"
    ], 
    "value": [
      "ANY"
    ]
  }, 
  "value": {
    "value": [
      "ANY"
    ], 
    "cr": [
      "CR"
    ], 
    "start": [
      "NL"
    ], 
    "end": [
      "EOS"
    ]
  }, 
  "end": {
    "__end": []
  }
}
'''
    doc = mermaid.state_diagram_parse_text(INI_MMD)
    actual = doc.transitions.from_transitions_json()
    print(actual)
    self.assert_string_equal_fuzzy( expected, actual, ignore_white_space = False )

if __name__ == '__main__':
  unit_test.main()
