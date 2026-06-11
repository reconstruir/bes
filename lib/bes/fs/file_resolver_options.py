#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.bcli.bcli_options import bcli_options
from bes.bcli.bcli_options_desc import bcli_options_desc
from bes.fs.file_ignore_options_mixin import file_ignore_options_mixin

from .file_sort_order import cli_file_sort_order_type

class _file_resolver_options_desc(bcli_options_desc):

  def _types(self):
    return [
      cli_file_sort_order_type,
    ]

  def _options_desc(self):
    return '''
    ignore_files  list[str]        default=None
           limit  int              default=None
  match_basename  bool             default=True
  match_function  callable         default=None
    match_patterns list[str]       default=None
        match_re  list[str]        default=None
      match_type  str              default=None
       recursive  bool             default=False
      sort_order  file_sort_order  default=None
    sort_reverse  bool             default=False
'''

class file_resolver_options(bcli_options, file_ignore_options_mixin):
  def __init__(self, **kwargs):
    super().__init__(_file_resolver_options_desc(), **kwargs)

file_resolver_options.register_check_class()
