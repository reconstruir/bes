#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple
from enum import IntEnum

from ..system.check import check
from bes.common.node import node
from bes.text.text_replace import text_replace
from bes.compat.StringIO import StringIO
from bes.text.string_list import string_list
from bes.text.text_line_parser import text_line_parser

from .comments import comments
from .white_space import white_space

class text_traversal(IntEnum):
  NODE = 1
  NODE_FLAT = 2
  CHILDREN_FLAT = 3
  CHILDREN_INLINE = 4
  
class tree_text_parser(object):

  @classmethod
  def parse(clazz, text, strip_comments = False, root_name = 'root', node_class = None):
    node_class = node_class or _text_node
    result = node_class(_text_node_data(root_name, 0))
    if not text:
      return result
    result.child_class = node_class
    st = _text_stack()
    current_indent_length = None
    text = comments.strip_muti_line_comment(text, '##[', ']##', replace = True)
    parser = text_line_parser(text)
    literals = clazz._fold_literals(parser)
    for line in parser:
      if line.text_is_empty(strip_comments = strip_comments):
        continue
      line_text = line.get_text(strip_comments = strip_comments, strip_text = True)
      line_text = clazz._resolve_literal(literals, line_text)
      if current_indent_length is None or line.indent_length > current_indent_length:
        st.push(line.indent_length, line_text, line.line_number)
      else:
        while not st.empty() and st.peek().depth >= line.indent_length:
          st.pop()
        st.push(line.indent_length, line_text, line.line_number)
      result.ensure_path(st.path())
      current_indent_length = line.indent_length
    return result

  @classmethod
  def _resolve_literal(clazz, literals, text):
    if text in literals:
      return literals[text].text
    return text
  
  _literal = namedtuple('_literal', 'id, text, line_number')
  @classmethod
  def _fold_literals(clazz, parser):
    'Fold all the lines in each literal into just one line with a literal id for text.'
    index = 0
    literal_index = 0
    result = {}
    while True:
      literal = clazz._find_next_literal(parser, index)
      if not literal:
        break
      literal_indent = ' ' * literal.marker_x
      literal_id = '@@tree_text_literal:%d@@' % (literal_index)
      indented_literal_id = '%s%s' % (literal_indent, literal_id)
      literal_lines = parser[literal.start_index : literal.end_index + 1]
      literal_lines = [ line.text[literal.text_x:] for line in literal_lines ]
      literal_text = '\n'.join(literal_lines)
      result[literal_id] = clazz._literal(literal_id, literal_text, parser[literal.start_index].line_number)
      parser.fold_by_indeces(literal.start_index, literal.end_index, indented_literal_id)
      index = literal.start_index + 1
      if index == len(parser):
        break
      literal_index += 1
    return result

  _literal_location = namedtuple('_literal_location', 'start_index, end_index, marker_x, text_x')
  @classmethod
  def _find_next_literal(clazz, parser, index):
    location = clazz._find_first_literal_start(parser, index)
    if not location:
      return None
    end_index = clazz._find_literal_end(parser, location)
    assert end_index >= location.start_index
    return clazz._literal_location(location.start_index, end_index, location.marker_x, location.text_x)

  @classmethod
  def _find_first_literal_start(clazz, parser, index):
    assert index >= 0
    assert index < len(parser)
    for i in range(index, len(parser)):
      line = parser[i]
      marker_x = clazz._find_literal_offset(line)
      if marker_x >= 0:
        # Find where the actual text begins following the ">" marker
        text_x = marker_x + 1
        for c in line.text[text_x:]:
          if not c.isspace():
            break
          text_x += 1
        return clazz._literal_location(i, None, marker_x, text_x)
    return None

  @classmethod
  def _find_literal_end(clazz, parser, location):
    'Find the line index for where a literal ends'
    # Iterate through lines starting with the line after the indent marker start.
    # compare the indent for each line against the text indent in the literal marker line
    # and if it fits include it in the literal until we run out of such lines.
    result = None
    for i in range(location.start_index + 1, len(parser)):
      line = parser[i]
      if not line.empty:
        text_indent = location.text_x - 1
        if line.indent_length <= text_indent:
          break
      result = i
    if result is None:
      result = len(parser) - 1
    return result
      
  @classmethod
  def _find_literal_offset(clazz, line):
    if not line.empty_no_comments:
      if line.text[line.indent_length] == '>':
        return line.indent_length
    return -1
      
class _text_node_data(namedtuple('_text_node_data', 'text, line_number')):
  def __new__(clazz, text, line_number):
    check.check_string(text)
    check.check_int(line_number)
    return clazz.__bases__[0].__new__(clazz, text, line_number)

  def clone_mutate_text(self, new_text):
    return self.__class__(new_text, self.line_number)

  @property
  def text_no_comments(self):
    return comments.strip_line(self.text, allow_quoted = False, strip_head = True, strip_tail = True)
  
class _text_node(node):

  def __init__(self, data):
    self._ensure_enum()
    super().__init__(data)

  @classmethod
  def _ensure_enum(clazz):
    if hasattr(clazz, '__enum_present'):
      return
    for e in text_traversal:
      setattr(clazz, e.name, e.value)
    setattr(clazz, '__enum_present', True)

  def find_child_by_text(self, text):
    return self.find_child(lambda node: node.data.text == text)

  def get_text(self, traversal, indent = None, delimiter = None):
    indent = indent or '  '
    delimiter = delimiter or ' '
    if traversal == self.NODE:
      result = self.data.text
    elif traversal == self.NODE_FLAT:
      result = self._get_text_node_flat(delimiter)
    elif traversal == self.CHILDREN_FLAT:
      result = self._get_text_children_flat(delimiter)
    elif traversal == self.CHILDREN_INLINE:
      result = self._get_text_children_inline(indent)
    else:
      raise ValueError('Invalid traversal: %s' % (str(traversal)))
    return result
  
  def _get_text_children_inline(self, indent):
    lines = []
    self._visit_node_text(0, True, indent, lines)
    if not lines:
      return []
    count = white_space.count_leading_spaces(lines[0])
    lines = [ line[count:] for line in lines ]
    return '\n'.join(lines) + '\n'

  def _get_text_node_flat(self, delimiter):
    buf = StringIO()
    self._node_text_collect(self, delimiter, buf)
    return buf.getvalue().strip()

  def _get_text_children_flat(self, delimiter):
    texts = [ child._get_text_node_flat(delimiter) for child in self.children ]
    return delimiter.join(texts)
  
  @classmethod
  def _node_text_collect(clazz, node, delimiter, buf):
    buf.write(node.data.text)
    if node.children:
      buf.write(delimiter)
    for i, child in enumerate(node.children):
      clazz._node_text_collect(child, delimiter, buf)
      buf.write(delimiter)
  
  def _visit_node_text(self, depth, children_only, indent, result):
    if not children_only:
      result.append('%s%s' % (indent * depth, self.data.text))
    for child in self.children:
      child._visit_node_text(depth + 1, False, indent, result)
    return result

  def replace_text(self, replacements):
    'Travese the tree and replace text in each node.'
    new_text = text_replace.replace(self.data.text, replacements, word_boundary = True)
    self.data = self.data.__class__(new_text, self.data.line_number)
    for child in self.children:
      child.replace_text(replacements)

class _text_stack(object):

  item = namedtuple('item', 'depth, data')

  def __init__(self):
    self._stack = []

  def push(self, depth, text, line_number):
    self._stack.append(self.item(depth, _text_node_data(text, line_number)))

  def pop(self):
    return self._stack.pop()

  def peek(self):
    return self._stack[-1]

  def empty(self):
    return len(self._stack) == 0

  def path(self):
    return [ i.data for i in self._stack ]

  def __str__(self):
    buf = StringIO()
    for i, item in enumerate(self._stack):
      if i != 0:
        buf.write('/')
      buf.write(str(item.depth or 0))
      buf.write(':')
      buf.write(item.data.text)
      buf.write(':')
      buf.write(item.data.line_number)
    return buf.getvalue()
