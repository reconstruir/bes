#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common import node
from bes.compat import StringIO
from collections import namedtuple
from .comments import comments
from .white_space import white_space

class _text_node(node):

  def __init__(self, data):
    super(_text_node, self).__init__(data)

  def find_child_by_text(self, text):
    return self.find_child(lambda node: node.data.text == text)

  def get_children_indented_text(self, indent = '  '):
    lines = []
    self._visit_node_text(0, True, indent, lines)
    if not lines:
      return []
    count = white_space.count_leading_spaces(lines[0])
    lines = [ line[count:] for line in lines ]
    return '\n'.join(lines) + '\n'
  
  def _visit_node_text(self, depth, children_only, indent, result):
    if not children_only:
      result.append('%s%s' % (indent * depth, self.data.text))
    for child in self.children:
      child._visit_node_text(depth + 1, False, indent, result)
    return result
  
class _text_stack(object):

  path_item = namedtuple('path_item', 'text, line_number')
  item = namedtuple('item', 'depth, path_item')

  def __init__(self):
    self._stack = []

  def push(self, depth, text, line_number):
    self._stack.append(self.item(depth, self.path_item(text, line_number)))

  def pop(self):
    return self._stack.pop()

  def peek(self):
    return self._stack[-1]

  def empty(self):
    return len(self._stack) == 0

  def path(self):
    return [ i.path_item for i in self._stack ]

  def __str__(self):
    buf = StringIO()
    for i, item in enumerate(self._stack):
      if i != 0:
        buf.write('/')
      buf.write(str(item.depth or 0))
      buf.write(':')
      buf.write(item.path_item.text)
      buf.write(':')
      buf.write(item.path_item.line_number)
    return buf.getvalue()
  
class tree_text_parser(object):

  @classmethod
  def parse(clazz, text, strip_comments = False):
    result = _text_node(_text_stack.path_item('root', 0))
    result.child_class = _text_node
    st = _text_stack()
    current_indent = None
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
  def node_text(clazz, node, include_root = False):
    if include_root:
      return child.to_string(data_func = lambda item: item.text)
    else:
      return '\n'.join([ child.to_string(data_func = lambda item: item.text) for child in node.children ])
  
  @classmethod
  def node_text_flat(clazz, node, delimiter = ' '):
    buf = StringIO()
    clazz._node_text_collect(node, delimiter, buf)
    return buf.getvalue().strip()

  @classmethod
  def node_children_text_flat(clazz, node, delimiter = ' '):
    texts = [ clazz.node_text_flat(child) for child in node.children ]
    return delimiter.join(texts)
  
  @classmethod
  def _node_text_collect(clazz, node, delimiter, buf):
    buf.write(node.data.text)
    if node.children:
      buf.write(delimiter)
    for i, child in enumerate(node.children):
      clazz._node_text_collect(child, delimiter, buf)
      buf.write(delimiter)
