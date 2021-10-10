#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import enum
from .checked_enum_mixin import checked_enum_mixin

class checked_enum(checked_enum_mixin, enum.Enum):
  'A IntEnum helper with methods for checking and parsing values'
  pass
