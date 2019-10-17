#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common.check import check
from bes.common.object_util import object_util
from bes.common.table import table
from bes.common.size import size
from bes.compat.StringIO import StringIO

from .text_box import text_box_unicode
from .white_space import white_space
  
class text_table_style(object):

  def __init__(self, spacing = None, box = None):
    self.spacing = check.check_int(spacing if spacing is not None else 1)
    self.box = check.check_text_box(box or text_box_unicode())
    
check.register_class(text_table_style)
    
class text_cell_renderer(object):

  JUST_LEFT = 'left'
  JUST_RIGHT = 'right'

  def __init__(self, just = None, width = None):
    self.just = just or self.JUST_LEFT
    self.width = width or 0

  def render(self, value, width = None, is_label = False):
    width = width or self.width or 0
    if value is not None:
      vs = self._value_to_string(value)
    else:
      vs = u''
    if self.just == self.JUST_LEFT:
      vs = vs.ljust(width)
    elif self.just == self.JUST_RIGHT:
      vs = vs.rjust(width)
    else:
      raise ValueError('Invalid just: %s' % (self.just))
    return vs

  def compute_width(self, value):
    return len(self.render(value, width = None))

  def _value_to_string(self, value):
    if not check.is_string(value):
      value = str(value)
    if self.width and len(value) > self.width:
      value = value[0:self.width]
    return value
  
class text_table(object):
  'A table of strings.'

  def __init__(self, width = None, height = None, data = None,
               style = None, column_spacing = None, cell_renderer = None):
    self._labels = None
    self._table = table(width = width, height = height, data = data)
    self._style = check.check_text_table_style(style or text_table_style())
    self._row_renderers = {}
    self._col_renderers = {}
    self._cell_renderers = {}
    self._default_cell_renderer = cell_renderer or text_cell_renderer()
    self._title = None
    
  def set_labels(self, labels):
    check.check_tuple(labels)
    self._table.check_width(len(labels))
    self._labels = labels[:]
    self.set_column_names(labels)

  def set_column_names(self, names):
    check.check_tuple(names)
    self._table.check_width(len(names))
    self._table.column_names = names

  def set_title(self, title):
    check.check_string(title)
    self._title = title

  def set(self, x, y, s):
    check.check_string(s)
    self._table.set(x, y, s)
    
  def get(self, x, y):
    return self._table.get(x, y)

  def __str__(self):
    return self.to_string()

  def to_string(self, strip_rows = False):
    spacing = self._style.spacing
    column_spacing = ' ' * spacing

    col_widths = self.column_widths()
    col_widths_with_spacing = [ (col + 2 * spacing) for col in col_widths ]
    num_cols = len(col_widths)

    box = self._style.box
    
    total_cols_width = sum(col_widths_with_spacing)
    h_middle_width = total_cols_width + (num_cols - 1) * box.v_bar.width
    h_width = box.tl_corner.width + h_middle_width + box.tr_corner.width

    buf = StringIO()
    
    if self._title:
      box.write_top(buf, h_width)
      buf.write('\n')
      box.write_centered_text(buf, h_width, self._title)
      buf.write('\n')
      if not self._labels:
        box.write_bottom(buf, h_width)
        buf.write('\n')
    
    if self._labels:
      box.write_middle(buf, h_width)
      buf.write('\n')
      buf.write(box.v_bar.char)
      for x in range(0, self._table.width):
        buf.write(column_spacing)
        self._write_label(x, buf, col_widths[x])
        buf.write(column_spacing)
        buf.write(box.v_bar.char)
      buf.write('\n')

    if not self._title or self._labels:
      box.write_top(buf, h_width)
      buf.write('\n')
      
    for y in range(0, self._table.height):
      row = self._table.row(y)
      assert len(row) == num_cols
      row_buf = StringIO()
      row_buf.write(box.l_bar.char)
      for x in range(0, self._table.width):
        row_buf.write(column_spacing)
        if x > 0:
          row_buf.write(box.v_bar.char)
          row_buf.write(column_spacing)
        self._write_cell(x, y, row_buf, col_widths[x])
      row_buf.write(column_spacing)
      row_buf.write(box.r_bar.char)
      row_str = row_buf.getvalue()
      if strip_rows:
        row_str = row_str.strip()
      buf.write(row_str)
      buf.write('\n')
    box.write_bottom(buf, h_width)
    buf.write('\n')
    value = buf.getvalue()
    # strip head and tail newlines
    return white_space.strip_new_lines(value)

  def _write_cell(self, x, y, stream, width):
    value = self._table.get(x, y)
    renderer = self.get_cell_renderer(x, y)
    assert renderer
    value_string = renderer.render(value, width = width)
    stream.write(value_string)
    return value_string
  
  def _write_label(self, x, stream, width):
    value = self._labels[x]
    renderer = self.get_cell_renderer(x, 0)
    assert renderer
    value_string = renderer.render(value, width = width, is_label = True)
    stream.write(value_string)
    return value_string
  
  def _column_width(self, x):
    self._table.check_x(x)
    max_col_width = self._max_column_width(x)
    if self._labels:
      max_col_width = max(max_col_width, len(self._labels[x]))
    return max_col_width
  
  def _max_column_width(self, x):
    self._table.check_x(x)
    max_width = 0
    for y in range(0, self._table.height):
      renderer = self.get_cell_renderer(x, y)
      value = self._table.get(x, y)
      max_width = max(max_width, renderer.compute_width(value))
    return max_width
  
  def sort_by_column(self, x):
    self._table.check_x(x)
    self._table.sort_by_column(x)

  def set_row(self, y, row):
    self._table.check_y(y)
    self._table.set_row(y, row)

  def set_row_renderer(self, y, renderer):
    self._table.check_y(y)
    self._row_renderers[y] = renderer

  def set_col_renderer(self, x, renderer):
    x = self._table.resolve_x(x)
    self._col_renderers[x] = renderer
    
  def set_cell_renderer(self, x, y, renderer):
    self._table.check_xy(x, y)
    self._cell_renderers[(x, y)] = renderer
    
  def get_cell_renderer(self, x, y):
    self._table.check_xy(x, y)
    return self._cell_renderers.get((x, y), None) or self._col_renderers.get(x, self._default_cell_renderer)

  def set_data(self, data):
    check.check_tuple_seq(data)
    self._table.set_data(data)

  def column_widths(self):
    return tuple([ self._column_width(x) for x in range(0, self._table.width) ])

  @property
  def default_cell_renderer(self):
    return self._default_cell_renderer
  
  @default_cell_renderer.setter
  def default_cell_renderer(self, renderer):
    if renderer:
      assert isinstance(renderer, text_cell_renderer)
    else:
      renderer = text_cell_renderer()
    self._default_cell_renderer = renderer
    #print('default renderer changed from %s to %s' % (self._default_cell_renderer, renderer))
