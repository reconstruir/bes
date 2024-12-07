#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.bcli.bcli_options import bcli_options
from bes.bcli.bcli_options_desc import bcli_options_desc

from bes.cli.cli_options import cli_options
from ..system.check import check
from bes.common.time_util import time_util
from bes.fs.file_ignore_options_mixin import file_ignore_options_mixin
from bes.property.cached_property import cached_property

from .file_resolver_options import file_resolver_options

class _files_cli_options_desc(bcli_options_desc):

  #@abstractmethod
  def _options_desc(self):
    return '''
                debug bool      default=False
              dry_run bool      default=False,
                quiet bool      default=False,
            recursive bool      default=False,
              verbose bool      default=False,
         ignore_files list[str] default=None
   dup_file_timestamp str       default=${_dup_file_timestamp}
       dup_file_count int       default=1
'''
  
  #@abstractmethod
  def _variables(self):
    return {
      '_dup_file_timestamp': lambda: time_util.timestamp(),
    }

  #@abstractmethod
  def _error_class(self):
    return IOError
  
class files_cli_options(bcli_options):
  def __init__(self, **kwargs):
    super().__init__(_files_cli_options_desc(), **kwargs)

  def pass_through_keys(self):
    return ( 'file_resolver_options', )
    
  @cached_property
  def file_resolver_options(self):
    return file_resolver_options(recursive = self.recursive,
                                 ignore_files = self.ignore_files)

files_cli_options.register_check_class()
