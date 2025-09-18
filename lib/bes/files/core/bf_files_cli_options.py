#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.bcli.bcli_options import bcli_options
from bes.bcli.bcli_options_desc import bcli_options_desc

from bes.system.check import check
from bes.common.time_util import time_util

class _bf_files_cli_options_desc(bcli_options_desc):

  #@abstractmethod
  def _options_desc(self):
    return '''
                debug bool  default=False
              dry_run bool  default=False
                quiet bool  default=False
            recursive bool  default=False
              verbose bool  default=False
      ignore_filename str   default=None
   dup_file_timestamp str   default=${_dup_file_timestamp}
       dup_file_count int   default=1
'''
  
  #@abstractmethod
  def _variables(self):
    return {
      '_dup_file_timestamp': lambda: time_util.timestamp(),
    }

  #@abstractmethod
  def _error_class(self):
    return IOError
  
class bf_files_cli_options(bcli_options):
  def __init__(self, **kwargs):
    super().__init__(_bf_files_cli_options_desc(), **kwargs)

bf_files_cli_options.register_check_class()
