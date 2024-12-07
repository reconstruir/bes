#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from datetime import datetime
from os import path

from bes.bcli.bcli_options import bcli_options
from bes.bcli.bcli_options_desc import bcli_options_desc

from ..system.check import check
from bes.script.blurber import blurber

from .files_cli_options import files_cli_options
from .files_cli_options import _files_cli_options_desc

class _file_split_options_desc(_files_cli_options_desc):

  #@abstractmethod
  def _options_desc(self):
    return self.combine_options_desc(super()._options_desc(), '''
          check_downloading bool      default=False
check_downloading_extension str       default=part
             check_modified bool      default=False
    check_modified_interval float     default=250.0
    existing_file_timestamp datetime  default=${_datetime_now}
          ignore_extensions list[str] default=None
                      unzip bool      default=False
          ignore_incomplete bool      default=False
''')
  
  #@abstractmethod
  def _variables(self):
    return self.combine_variables(super()._variables(), {
      '_datetime_now': lambda: datetime.now(),
    })

class file_split_options(bcli_options):
  def __init__(self, **kwargs):
    super().__init__(_file_split_options_desc(), **kwargs)

file_split_options.register_check_class()
