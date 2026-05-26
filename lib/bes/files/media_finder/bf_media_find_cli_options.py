#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.bcli.bcli_options import bcli_options
from bes.bcli.bcli_options_desc import bcli_options_desc
from bes.system.check import check

from .bf_media_feature_resolver_registry import bf_media_feature_resolver_registry
from .bf_media_finder_options import _bf_media_cli_sort_type, _bf_media_cli_media_type
from .bf_media_finder_options import bf_media_finder_options
from .bf_media_sort_type import bf_media_sort_type

class _bf_media_find_cli_options_desc(bcli_options_desc):

  #@abstractmethod
  def _types(self):
    return [
      _bf_media_cli_sort_type,
      _bf_media_cli_media_type,
    ]

  #@abstractmethod
  def _options_desc(self):
    return '''
      media_types  bf_media_type      default=all
        sort_type  bf_media_sort_type default=found_order
      ignore_file  str                default=.bes_ignore
   case_sensitive  bool               default=False
    sort_reversed  bool               default=False
 feature_resolver  str
          verbose  bool               default=False
            count  bool               default=False
            debug  bool               default=False
'''

  #@abstractmethod
  def _error_class(self):
    from bes.files.core.bf_error import bf_error
    return bf_error

class bf_media_find_cli_options(bcli_options):
  def __init__(self, **kwargs):
    super().__init__(_bf_media_find_cli_options_desc(), **kwargs)

  def __setattr__(self, name, value):
    if name == 'sort_type' and isinstance(value, str):
      try:
        value = bf_media_sort_type.parse(value.strip().lower())
      except ValueError:
        object.__getattribute__(self, '_options')[name] = value
        return
    super().__setattr__(name, value)

  def pass_through_keys(self):
    return ( 'finder_options', )

  @property
  def finder_options(self):
    resolver = None
    if self.feature_resolver:
      try:
        resolver = bf_media_feature_resolver_registry.get(self.feature_resolver)
      except KeyError:
        from bes.files.core.bf_error import bf_error
        raise bf_error(f'unknown feature resolver: "{self.feature_resolver}"')
    return bf_media_finder_options(
      media_types      = self.media_types,
      sort_type        = self.sort_type,
      ignore_file      = self.ignore_file,
      case_sensitive   = self.case_sensitive,
      sort_reversed    = self.sort_reversed,
      feature_resolver = resolver,
    )

bf_media_find_cli_options.register_check_class()
