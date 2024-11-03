#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os

from ..system.check import check
from bes.common.json_util import json_util
from bes.common.table import table
from bes.common.tuple_util import tuple_util
from bes.fs.file_util import file_util
from bes.system.console import console
from bes.text.line_break import line_break
from bes.text.text_box import text_box_colon
from bes.text.text_box import text_box_unicode
from bes.text.text_box import text_box_space
from bes.text.text_box import text_box_ascii
from bes.text.text_table import text_cell_renderer
from bes.text.text_table import text_table
from bes.text.text_table import text_table_style

from .data_output_options import data_output_options
from .data_output_style import data_output_style

class data_output(object):

  @classmethod
  def output_table(clazz, data, options = None, stream = None):
    check.check_data_output_options(options, allow_none = True)

    options = options or data_output_options()
    if stream:
      clazz._output_table_to_stream(data, stream, options)
    else:
      with file_util.open_with_default(filename = options.output_filename) as fout:
        clazz._output_table_to_stream(data, fout, options)
      
  @classmethod
  def _output_table_to_stream(clazz, data, stream, options):
    if options.style == data_output_style.BRIEF:
      for item in data:
        stream.write(str(item[options.brief_column]))
        stream.write(line_break.DEFAULT_LINE_BREAK)
    elif options.style == data_output_style.JSON:
      data = clazz._normalize_table_for_structured_data(data)
      stream.write(json_util.to_json(data, indent = 2, sort_keys = True))
    elif options.style == data_output_style.CSV:
      for item in data:
        item = clazz._normalize_table_item(item)
        stream.write(options.csv_delimiter.join(item))
        stream.write(line_break.DEFAULT_LINE_BREAK)
    elif options.style in [ data_output_style.TABLE, data_output_style.PLAIN_TABLE ]:
      data = clazz._normalize_data(data)
      table_data = table(data = data, column_names = options.column_names)
      if table_data.empty:
        return
      is_plain = options.style == data_output_style.PLAIN_TABLE
      if is_plain:
        table_style = text_table_style(spacing = 1, box = text_box_space())
      else:
        #table_style = text_table_style(spacing = 1, box = text_box_unicode())
        table_style = text_table_style(spacing = 1, box = text_box_ascii())

      column_names = None
      if options.column_names:
        column_names = list(options.column_names)
      for column in sorted(options.remove_columns or [], reverse = True):
        table_data.remove_column(column)
        if column_names:
          column_names.remove(column)
      if column_names:
        column_names = tuple(column_names)
      tt = text_table(data = table_data, style = table_style)
      if column_names:
        if not is_plain:
          tt.set_labels(column_names)
        tt.set_column_names(column_names)
      if options.table_cell_renderers:
        for column_name, renderer in options.table_cell_renderers.items():
          tt.set_col_renderer(column_name, renderer)
      if options.table_title and not is_plain:
        tt.set_title(options.table_title)

      text = str(tt)
      if options.table_flexible_column:
        flexible_index = table_data.resolve_x(options.table_flexible_column)
        lines = text.split(line_break.DEFAULT_LINE_BREAK)
        render_width = len(lines[0])

        try:
          terminal_width = console.terminal_width()
        except Exception as ex:
          terminal_width = None

        if terminal_width != None:
          max_column_width = tt._max_column_width(flexible_index)
          if terminal_width < render_width:
            overflow = render_width - terminal_width + 1
            new_column_width = max(max_column_width - overflow, 0)
          else:
            new_column_width = max_column_width
          
          tt.set_col_renderer(options.table_flexible_column, text_cell_renderer(width = new_column_width))
          text = str(tt)
      
      stream.write(text)
      stream.write(line_break.DEFAULT_LINE_BREAK)
    else:
      raise RuntimeError('Unhandled data output style: {}'.format(style))

  @classmethod
  def _output_string_to_stream(clazz, s, stream):
    stream.write(s)
    
  @classmethod
  def _normalize_data(clazz, data):
    if isinstance(data, dict):
      return clazz._normalize_dict(data)
    return data

  @classmethod
  def _normalize_table_item(clazz, item):
    if check.is_tuple(item) or check.is_list(item):
      return tuple([ str(x) for x in item])
    return item
  
  @classmethod
  def _normalize_dict(clazz, data):
    assert isinstance(data, dict)
    return [ item for item in data.items() ]

  @classmethod
  def _normalize_table_for_structured_data(clazz, data):
    result = []
    for item in data:
      if tuple_util.is_named_tuple(item):
        item = tuple_util.named_tuple_to_dict(item)
      result.append(item)
    return result
  
  @classmethod
  def output_value(clazz, data, key, options = None):
    check.check_dict(data)
    check.check_string(key)
    check.check_data_output_options(options, allow_none = True)

    options = options or data_output_options()
    with file_util.open_with_default(filename = options.output_filename) as fout:
      if options.style == data_output_style.BRIEF:
        value = data[key]
        clazz._output_string_to_stream(str(value) + os.linesep, fout)
      else:
        clazz._output_table_to_stream(data, fout, options)
