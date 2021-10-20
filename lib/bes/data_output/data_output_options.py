#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import pprint

from bes.common.check import check

from .data_output_style import data_output_style

class data_output_options(object):
  
  def __init__(self, *args, **kargs):
    self.brief_column = 0
    self.output_filename = None
    self.style = data_output_style.TABLE
    self.plain_delimiter = ','
    for key, value in kargs.items():
      setattr(self, key, value)
    check.check_int(self.brief_column)
    check.check_string(self.output_filename, allow_none = True)
    self.style = check.check_data_output_style(self.style, allow_none = True)
    check.check_string(self.plain_delimiter)

  def __str__(self):
    return pprint.pformat(self.__dict__)
    
check.register_class(data_output_options)
