#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common import check, node, string_util
from bes.compat import StringIO
from bes.enum import enum
from collections import namedtuple

from .comments import comments
from .white_space import white_space

class text_traversal(enum):
  NODE = 1
  NODE_FLAT = 2
  CHILDREN_FLAT = 3
  CHILDREN_INLINE = 4

class _text_node_data(namedtuple('_text_node_data', 'text, line_number')):
  def __new__(clazz, text, line_number):
    check.check_string(text)
    check.check_int(line_number)
    return clazz.__bases__[0].__new__(clazz, text, line_number)

  def clone_mutate_text(self, new_text):
    return self.__class__(new_text, self.line_number)

  @property
  def text_no_comments(self):
    return comments.strip_line(self.text, strip_head = True, strip_tail = True)
  
class _text_node(node):

  def __init__(self, data):
    self._ensure_enum()
    super(_text_node, self).__init__(data)

  @classmethod
  def _ensure_enum(clazz):
    if hasattr(clazz, '__enum_present'):
      return
    for name, value in text_traversal:
      setattr(clazz, name, value)
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
    new_text = string_util.replace(self.data.text, replacements)
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
  
class tree_text_parser(object):

  @classmethod
  def parse(clazz, text, strip_comments = False, root_name = 'root'):
    result = _text_node(_text_node_data(root_name, 0))
    result.child_class = _text_node
    st = _text_stack()
    current_indent = None
    text = comments.strip_muti_line_comment(text, '##[', ']##', replace = True)
    for i, line in enumerate(text.split('\n')):
      if strip_comments:
        line = comments.strip_line(line)
      if not line or line.isspace():
        continue
      line_number = i + 1
      indent = clazz._count_indent(line)
      line = line.strip()
      if current_indent is None or indent > current_indent:
        st.push(indent, line, line_number)
      else:
        while not st.empty() and st.peek().depth >= indent:
          st.pop()
        st.push(indent, line, line_number)
      result.ensure_path(st.path())
      current_indent = indent
    return result
  
  @classmethod
  def _count_indent(clazz, s):
    count = 0
    for c in s:
      if c == ' ':
        count += 1
      elif c == '\t':
        count += 2
      else:
        break
    return count

  @classmethod
  def make_node(clazz, text, line_number):
    return _text_node(_text_node_data(text, line_number))
  
