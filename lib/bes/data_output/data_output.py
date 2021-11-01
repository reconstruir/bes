#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import pprint
from bes.common.check import check

from bes.common.json_util import json_util
from bes.common.tuple_util import tuple_util
from bes.fs.file_util import file_util
from bes.text.line_break import line_break
from bes.text.text_table import text_table

from .data_output_options import data_output_options
from .data_output_style import data_output_style

class data_output(object):

  @classmethod
  def output_table(clazz, data, options = None):
    check.check_data_output_options(options, allow_none = True)

    options = options or data_output_options()
    with file_util.open_with_default(filename = options.output_filename) as fout:
      clazz._output_table_to_stream(data, fout, options)
      
  @classmethod
  def _output_table_to_stream(clazz, data, stream, options):
    if options.style == data_output_style.BRIEF:
      for item in data:
        stream.write(str(item[options.brief_column]))
        stream.write(line_break.DEFAULT_LINE_BREAK)
    elif options.style == data_output_style.JSON:
      data = clazz._normalize_structured_data(data)
      stream.write(json_util.to_json(data, indent = 2, sort_keys = True))
    elif options.style == data_output_style.CSV:
      for item in data:
        item = clazz._normalize_table_item(item)
        stream.write(options.csv_delimiter.join(item))
        stream.write(line_break.DEFAULT_LINE_BREAK)
    elif options.style == data_output_style.TABLE:
      data = clazz._normalize_data(data)
      tt = text_table(data = data)
      stream.write(str(tt))
      stream.write(line_break.DEFAULT_LINE_BREAK)

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
  def _normalize_structured_data(clazz, data):
    result = []
    for item in data:
      if tuple_util.is_named_tuple(item):
        item = tuple_util.named_tuple_to_dict(item)
      result.append(item)
    return result
  
