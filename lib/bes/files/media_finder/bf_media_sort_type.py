#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.enum_util.checked_enum import checked_enum

class bf_media_sort_type(checked_enum):
  FOUND_ORDER    = 'found_order'
  NAME           = 'name'
  PATH           = 'path'
  DATE           = 'date'
  SIZE           = 'size'
  KIND           = 'kind'
  # Tier 2 — not yet implemented
  RESOLUTION     = 'resolution'
  WIDTH          = 'width'
  HEIGHT         = 'height'
  ASPECT_RATIO   = 'aspect_ratio'
  DURATION       = 'duration'
  AVERAGE_HASH   = 'average_hash'

  @property
  def is_slow(self):
    return self in _SLOW_SORT_TYPES

_SLOW_SORT_TYPES = frozenset([
  bf_media_sort_type.RESOLUTION,
  bf_media_sort_type.WIDTH,
  bf_media_sort_type.HEIGHT,
  bf_media_sort_type.ASPECT_RATIO,
  bf_media_sort_type.DURATION,
  bf_media_sort_type.AVERAGE_HASH,
])

bf_media_sort_type.register_check_class()
