#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

from ..system.check import check
from ..text.lexer_token import lexer_token
from ..text.text_line_parser import text_line_parser
from ..text.white_space import white_space
from ..common.point import point

class mermaid(object):

  @classmethod
  def parse_state_diagram_text(clazz, text, indent = 2):
    check.check_string(text)
    check.check_int(indent)

    tokens = clazz._state_diagram_tokenize(text, indent)
    states = set()
    for token in tokens:
      if token.token_type == 'transition':
        to_state = token.value.to_state
        from_state = token.value.from_state
        if to_state == '[*]':
          to_state = '__end'
        if from_state == '[*]':
          from_state = '__start'
        #print(f'{from_state} --> {to_state}')
        states.add(to_state)
        states.add(from_state)
    return sorted(list(states))

  @classmethod
  def _state_diagram_tokenize(clazz, text, indent):
    check.check_string(text)
    check.check_int(indent)

    lines = text_line_parser.parse_lines(text,
                                         strip_comments = False,
                                         strip_text = False,
                                         remove_empties = False)
    tokens = []
    for line_number, line in enumerate(lines, start = 1):
      token = clazz._parse_state_diagram_line(line, line_number, indent)
      tokens.append(token)  
    return tokens
  
  @classmethod
  def _parse_state_diagram_line(clazz, line, line_number, indent):
    count = white_space.count_leading_spaces(line)
    sline = line.strip()
    #print(f'line="{line}" sline="{sline}" count={count}')

    if len(sline) == 0:
      return lexer_token(token_type = 'empty_line',
                         value = line,
                         position = point(count, line_number))

    elif sline.startswith('%%'):
      return lexer_token(token_type = 'comment',
                         value = line,
                         position = point(count, line_number))
    elif count == 0:
      if sline == 'stateDiagram-v2':
        return lexer_token(token_type = 'diagram_type',
                           value = 'stateDiagram-v2',
                           position = point(0, line_number))
    elif (count % indent) == 0:
      return clazz._parse_state_diagram_directive(count, line, sline, line_number)
    else:
      raise RuntimeError(f'Invalid indent: "{line}"')

  @classmethod
  def _parse_state_diagram_directive(clazz, count, line, sline, line_number):
    if '-->' in line:
      transition = clazz._parse_state_diagram_transition(line)
      return lexer_token(token_type = 'transition',
                         value = transition,
                         position = point(count, line_number))
    else:
      return lexer_token(token_type = 'unknown',
                         value = line,
                         position = point(count, line_number))
    
  _transition = namedtuple('_transition', 'line, from_state, to_state')
  @classmethod
  def _parse_state_diagram_transition(clazz, line):
    left, delimiter, right = line.partition('-->')
    assert delimiter == '-->'
    from_state = left.strip()
    to_state = clazz._parse_state_diagram_transition_to_state(right)
    return clazz._transition(line, from_state, to_state)

  @classmethod
  def _parse_state_diagram_transition_to_state(clazz, line):
    left, delimiter, right = line.partition(':')
    assert delimiter in ( ':', '' )
    return left.strip()
