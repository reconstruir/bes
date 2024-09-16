#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.bcli.bcli_options import bcli_options
from bes.bcli.bcli_options_desc import bcli_options_desc

from bes.bcli.bcli_type_i import bcli_type_i

from .bf_file_matcher_type import bf_cli_file_matcher_type
from ..bf_path_type import bf_cli_path_type

class _bf_file_matcher_options_desc(bcli_options_desc):

  #@abstractmethod
  def types(self):
    return [
      bf_cli_file_matcher_type,
      bf_cli_path_type,
    ]

  #@abstractmethod
  def options_desc(self):
    return '''
ignore_case bool                 default=False
 match_type bf_file_matcher_type default=ANY
  path_type bf_path_type         default=ABSOLUTE
'''
  
class bf_file_matcher_options(bcli_options):
  def __init__(self, **kwargs):
    super().__init__(_bf_file_matcher_options_desc(), **kwargs)
    
bf_file_matcher_options.register_check_class()
