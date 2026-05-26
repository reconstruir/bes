#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.bcli.bcli_options import bcli_options
from bes.bcli.bcli_options_desc import bcli_options_desc
from bes.bcli.bcli_type_checked_enum import bcli_type_checked_enum
from bes.system.check import check

from .bf_media_sort_type import bf_media_sort_type

class _bf_media_cli_sort_type(bcli_type_checked_enum):
  __enum_class__ = bf_media_sort_type

class _bf_media_cli_media_type(bcli_type_checked_enum):
  # Reuses checked_enum machinery but maps 'all' → frozenset, 'image' → frozenset, etc.
  # Since bf_media_sort_type is an enum but media_type is a frozenset, we handle
  # parse/check manually.
  @classmethod
  def name_str(clazz):
    return 'bf_media_type'

  @classmethod
  def type_function(clazz):
    return frozenset

  @classmethod
  def parse(clazz, text):
    text = text.strip().lower()
    if text == 'all':
      return frozenset(['image', 'video'])
    if text == 'image':
      return frozenset(['image'])
    if text == 'video':
      return frozenset(['video'])
    raise ValueError(f'invalid media type: "{text}" — expected image, video, or all')

  @classmethod
  def check(clazz, value, allow_none=False):
    if value is None and allow_none:
      return None
    if not isinstance(value, frozenset):
      raise TypeError(f'expected frozenset, got {type(value)}')
    return value

class _bf_media_finder_options_desc(bcli_options_desc):

  #@abstractmethod
  def _types(self):
    return [
      _bf_media_cli_sort_type,
      _bf_media_cli_media_type,
    ]

  #@abstractmethod
  def _options_desc(self):
    return '''
         media_types  bf_media_type  default=all
           sort_type  bf_media_sort_type  default=found_order
       sort_reversed  bool  default=False
         ignore_file  str  default=.bes_ignore
      case_sensitive  bool  default=False
       attr_resolver  type
    num_scan_workers  int  default=2
     scan_chunk_size  int  default=50
 num_resolve_workers  int  default=2
   resolve_chunk_size int  default=10
'''

  #@abstractmethod
  def _error_class(self):
    from bes.files.core.bf_error import bf_error
    return bf_error

class bf_media_finder_options(bcli_options):
  def __init__(self, **kwargs):
    super().__init__(_bf_media_finder_options_desc(), **kwargs)

  def __setattr__(self, name, value):
    if name == 'sort_type' and isinstance(value, str):
      try:
        value = bf_media_sort_type.parse(value.strip().lower())
      except ValueError:
        # Extended sort type — store directly, bypassing framework type check
        object.__getattribute__(self, '_options')[name] = value
        return
    super().__setattr__(name, value)

bf_media_finder_options.register_check_class()
