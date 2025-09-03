#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.bcli.bcli_options import bcli_options
from bes.bcli.bcli_options_desc import bcli_options_desc

from bes.system.check import check
from bes.property.cached_property import cached_property

from ..find.bf_file_finder_options import _bf_file_finder_options_desc
from ..find.bf_file_finder_mode import bf_cli_file_finder_mode

from ..bf_entry_sort_criteria import bf_entry_sort_criteria_bcli

from .bf_file_resolver_entry import bf_file_resolver_entry

class _bf_file_resolver_options_desc(bcli_options_desc):

  #@abstractmethod
  def _types(self):
    return [
      bf_entry_sort_criteria_bcli,
      bf_cli_file_finder_mode,
    ]

  #@abstractmethod
  def _variables(self):
    return {
      '_bf_file_resolver_entry_default_type': lambda: bf_file_resolver_entry,
    }
  
  #@abstractmethod
  def _options_desc(self):
    return '''
mode                   bf_file_finder_mode    default=IMMEDIATE
sort_order             bf_entry_sort_criteria default=FILENAME
entry_class            type                   default=${_bf_file_resolver_entry_default_type}
match_function         callable
'''
  
  #@abstractmethod
  def _error_class(self):
    return bf_file_resolver_error
  
class bf_file_resolver_options(bcli_options):
  def __init__(self, **kwargs):
    super().__init__(_bf_file_resolver_options_desc(), **kwargs)

bf_file_resolver_options.register_check_class()
