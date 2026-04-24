#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.bcli.bcli_options import bcli_options
from bes.bcli.bcli_options_desc import bcli_options_desc

from .bf_checksum_error import bf_checksum_error

class _bf_checksum_command_options_desc(bcli_options_desc):

  #@abstractmethod
  def _types(self):
    return []

  #@abstractmethod
  def _options_desc(self):
    return '''
  verbose   bool  default=False
    debug   bool  default=False
algorithm    str  default=sha256
'''

  #@abstractmethod
  def _error_class(self):
    return bf_checksum_error

class bf_checksum_command_options(bcli_options):
  def __init__(self, **kwargs):
    super().__init__(_bf_checksum_command_options_desc(), **kwargs)

bf_checksum_command_options.register_check_class()
