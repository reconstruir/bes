#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from typing import Any, ClassVar

from .bf_media_attr_not_available import _bf_attr_not_available_type

class bf_media_attr_resolver_base:
  'Abstract base for media attribute resolvers. No external dependencies allowed here.'

  name: ClassVar[str]  # unique resolver name, e.g. 'pil_av'

  @classmethod
  def resolve(cls, filename: str, mime_type: str, attr_name: str) -> Any:
    '''
    Resolve a single attribute for one file.
    Returns: computed value, BF_ATTR_NOT_AVAILABLE (tried but no data), or None (attr not handled).
    '''
    raise NotImplementedError

  @classmethod
  def attr_sort_key(cls, value) -> tuple:
    'Wrap value in a sort key that places real values before None/NOT_AVAILABLE.'
    if value is None or isinstance(value, _bf_attr_not_available_type):
      return (1, None)
    return (0, value)
