#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.bcli.bcli_options import bcli_options
from bes.bcli.bcli_options_desc import bcli_options_desc

from .mermaid_error import mermaid_error

class _mermaid_options_desc(bcli_options_desc):
  def _options_desc(self):
    return '''
  debug    bool  default=False
  verbose  bool  default=False
'''
  def _error_class(self): return mermaid_error

class mermaid_options(bcli_options):
  def __init__(self, **kwargs):
    super().__init__(_mermaid_options_desc(), **kwargs)

mermaid_options.register_check_class()
