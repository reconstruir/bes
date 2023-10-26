#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple
import os.path as path

from ..common.point import point
from ..fs.file_check import file_check
from ..fs.file_util import file_util
from ..system.check import check
from ..text.lexer_token import lexer_token
from ..text.text_line_parser import text_line_parser
from ..text.white_space import white_space

class mermaid(object):

  @classmethod
  def state_diagram_parse_file(clazz, filename, indent = 2):
    filename = file_check.check_file(filename)
    check.check_int(indent)

    text = file_util.read(filename, codec = 'utf-8')
    return clazz.state_diagram_parse_text(text, indent = indent)

  _HEADER = '''
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.text.text_lexer_base import text_lexer_base
from bes.text.text_lexer_state_base import text_lexer_state_base
'''

  _LEXER_CLASS_TEMPLATE = '''
class {namespace}_{name}_lexer_base(text_lexer_base):
  def __init__(self, {name}, source = None):
    super().__init__(log_tag, source = source)

'''

  _STATE_CLASS_TEMPLATE = '''
class {namespace}_{name}_lexer_state_{state}(text_lexer_state_base):
  def __init__(self, lexer):
    super().__init__(lexer)

  def handle_char(self, c):
    self.log_handle_char(c)
'''
  
  @classmethod
  def state_diagram_generate_code(clazz, filename, namespace, name, output_directory, indent = 2):
    filename = file_check.check_file(filename)
    check.check_string(namespace)
    check.check_string(name)
    check.check_string(output_directory)
    check.check_int(indent)

    states = clazz.state_diagram_parse_file(filename, indent = indent)
    basename = f'{namespace}_{name}_lexer_detail.py'
    output_filename = path.join(output_directory, basename)
    file_util.mkdir(output_directory)
    with open(output_filename, 'w') as stream:
      stream.write(clazz._HEADER)
      stream.write('\n')
      caca = []
      for state in states:
        state_class_code = clazz._STATE_CLASS_TEMPLATE.format(namespace = namespace,
                                                              name = name,
                                                              state = state)
        stream.write(state_class_code)
        stream.write('\n')
        state_class_name = f'{namespace}_{name}_lexer_state_{state}'
        state_instance_code = f'self.{state} = {state_class_name}(self)'
        caca.append(state_instance_code)
      lexer_class_code = clazz._LEXER_CLASS_TEMPLATE.format(namespace = namespace,
                                                            name = name,
                                                            state = state)
      for c in caca:
        stream.write('    ')
        stream.write(c)
        stream.write('\n')
    return output_filename

  @classmethod
  def state_diagram_parse_text(clazz, text, indent = 2):
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
      token = clazz._state_diagram_parse_line(line, line_number, indent)
      tokens.append(token)  
    return tokens
  
  @classmethod
  def _state_diagram_parse_line(clazz, line, line_number, indent):
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
      return clazz._state_diagram_parse_directive(count, line, sline, line_number)
    else:
      raise RuntimeError(f'Invalid indent: "{line}"')

  @classmethod
  def _state_diagram_parse_directive(clazz, count, line, sline, line_number):
    if '-->' in line:
      transition = clazz._state_diagram_parse_transition(line)
      return lexer_token(token_type = 'transition',
                         value = transition,
                         position = point(count, line_number))
    else:
      return lexer_token(token_type = 'unknown',
                         value = line,
                         position = point(count, line_number))
    
  _transition = namedtuple('_transition', 'line, from_state, to_state')
  @classmethod
  def _state_diagram_parse_transition(clazz, line):
    left, delimiter, right = line.partition('-->')
    assert delimiter == '-->'
    from_state = left.strip()
    to_state = clazz._state_diagram_parse_transition_to_state(right)
    return clazz._transition(line, from_state, to_state)

  @classmethod
  def _state_diagram_parse_transition_to_state(clazz, line):
    left, delimiter, right = line.partition(':')
    assert delimiter in ( ':', '' )
    return left.strip()
