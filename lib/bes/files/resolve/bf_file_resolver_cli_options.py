#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import getpass

from bes.bcli.bcli_options import bcli_options
from bes.bcli.bcli_options_desc import bcli_options_desc
from bes.credentials.credentials import credentials

from ..bf_file_type import bf_cli_file_type

from .bf_file_resolver_error import bf_file_resolver_error

class _bf_file_resolver_cli_options_desc(bcli_options_desc):


  #@abstractmethod
  def _types(self):
    return [
      bf_cli_file_type,
    ]
  
  #@abstractmethod
  def _options_desc(self):
    return '''
verbose   bool         default=False
debug     bool         default=False
quiet     bool         default=False
quit      bool         default=False
 name     str
file_type bf_file_type default=FILE_OR_LINK
                 max_depth int
                 min_depth int
                stop_after int
'''

  #@abstractmethod
  def _error_class(self):
    return bf_file_resolver_error
  
class bf_file_resolver_cli_options(bcli_options):
  def __init__(self, **kwargs):
    super().__init__(_bf_file_resolver_cli_options_desc(), **kwargs)

bf_file_resolver_cli_options.register_check_class()
