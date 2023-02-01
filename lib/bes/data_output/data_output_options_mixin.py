#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from ..system.check import check
from bes.fs.file_check import file_check
from bes.property.cached_property import cached_property

from .data_output_options import data_output_options

class data_output_options_mixin(object):

  def __init__(self):
    pass

  @cached_property  
  def data_output_options(self):
    return data_output_options(output_filename = self.output_filename,
                               style = self.output_style,
                               limit_num_items = self.limit_num_items,
                               raw = self.raw)
