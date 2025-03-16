#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import json
import os
import pickle
import base64

from ..common.json_util import json_util
from ..common.type_checked_list import type_checked_list
from ..data_output.data_output import data_output
from ..data_output.data_output_options import data_output_options
from ..data_output.data_output_style import data_output_style
from ..files.bf_check import bf_check
from ..files.bf_file_ops import bf_file_ops
from ..system.check import check

class bdata_class_list_base(type_checked_list):

  def to_dict_list(self):
    return [ item.to_dict() for item in self ]

  def to_table(self):
    return [ item.to_tuple() for item in self ]
  
  def to_json(self):
    d = [ item.to_dict() for item in self ]
    return json_util.to_json(d,
                             indent = 2,
                             sort_keys = False,
                             ensure_last_line_sep = True)

  @classmethod
  def parse_json_text(clazz, json_text, source):
    check.check_string(json_text)

    dict_items = json.loads(json_text)
    return clazz.parse_dict_list(dict_items, source)

  @classmethod
  def parse_dict_list(clazz, dict_items, source):
    check.check_seq(dict_items, dict)
    check.check_string(source)

    value_type = getattr(clazz, '__value_type__', None)
    if not value_type:
      raise clazz.error_class('No clazz attribute "__value_type__" found in "{clazz}"')

    result = clazz()
    for next_dict_item in dict_items:
      item = value_type.parse_json_dict(next_dict_item, source)
      result.append(item)
    return result

  @classmethod
  def read_json_file(clazz, filename):
    bf_check.check_file(filename)

    dict_items = json_util.read_file(filename)
    return clazz.parse_dict_list(dict_items, filename)

  def save_json_file(self, filename):
    check.check_string(filename)

    json_util.save_file(filename,
                        self.to_dict_list(),
                        indent = 2,
                        ensure_last_line_sep = True)

  def output(self, options = None):
    check.check_data_output_options(options, allow_none = True, default_value_class = data_output_options)

    with bf_file_ops.open_with_default(filename = options.output_filename) as fout:
      if options.style == data_output_style.JSON:
        fout.write(self.to_json())
      elif options.style == data_output_style.BRIEF:
        for item in self:
          fout.write(str(item))
      elif options.style == data_output_style.TABLE:
        data_output.output_table(self.to_table(), options = options, stream = fout)

  def to_pickle(self):
    l = self.to_dict_list()
    return pickle.dumps(l)

  def to_base64_pickle(self):
    p = self.to_pickle()
    return base64.b64encode(p)

  @classmethod
  def read_pickle_bytes(clazz, pickle_bytes, source):
    check.check_bytes(pickle_bytes)
    check.check_string(source)

    dict_items = pickle.loads(pickle_bytes)
    return clazz.parse_dict_list(dict_items, source)

  @classmethod
  def read_pickle_file(clazz, filename, source):
    bf_check.check_file(filename)

    pickle_data = bf_file_ops.read(filename)
    return clazz.read_pickle_bytes(pickle_data, source)
    
  def save_pickle_file(self, filename):
    check.check_string(filename)

    pickle_data = self.to_pickle()
    bf_file_ops.save(filename, content = pickle_data)
    
check.register_class(bdata_class_list_base, include_seq = False)
