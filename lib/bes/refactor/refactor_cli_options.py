#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.bcli.bcli_options import bcli_options
from bes.bcli.bcli_options_desc import bcli_options_desc

from .refactor_error import refactor_error

class _refactor_cli_options_desc(bcli_options_desc):

  #@abstractmethod
  def _types(self):
    return []

  #@abstractmethod
  def _options_desc(self):
    return '''
verbose       bool  default=False
debug         bool  default=False
dry_run       bool  default=False
word_boundary bool  default=False
try_git       bool  default=False
unsafe        bool  default=False
backup        bool  default=False
'''

  #@abstractmethod
  def _error_class(self):
    return refactor_error

class refactor_cli_options(bcli_options):
  def __init__(self, **kwargs):
    super().__init__(_refactor_cli_options_desc(), **kwargs)

refactor_cli_options.register_check_class()
