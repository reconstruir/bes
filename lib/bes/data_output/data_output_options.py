#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import pprint

from ..system.check import check
from bes.text.text_table import text_cell_renderer

from .data_output_style import data_output_style

class data_output_options(object):
  
  def __init__(self, *args, **kargs):
    self.limit_num_items = None
    self.brief_column = 0
    self.output_filename = None
    self.style = data_output_style.TABLE
    self.csv_delimiter = ','
    self.remove_columns = None
    self.column_names = None
    self.table_cell_renderers = None
    self.table_title = None
    self.table_flexible_column = None
    for key, value in kargs.items():
      setattr(self, key, value)
    check.check(self.brief_column, check.INTEGER_OR_STRING_TYPES)
    check.check_string(self.output_filename, allow_none = True)
    self.style = check.check_data_output_style(self.style, allow_none = True)
    check.check_string(self.csv_delimiter)
    check.check_tuple(self.remove_columns, allow_none = True, value_type = check.INTEGER_OR_STRING_TYPES)
    check.check_tuple(self.column_names, allow_none = True, value_type = check.STRING_TYPES)
    check.check_dict(self.table_cell_renderers,
                     key_type = check.STRING_TYPES,
                     value_type = text_cell_renderer,
                     allow_none = True)
    check.check_string(self.table_title, allow_none = True)
    check.check_string(self.table_flexible_column, allow_none = True)

  def __str__(self):
    return pprint.pformat(self.__dict__)
    
check.register_class(data_output_options)
