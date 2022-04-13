#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from ..system.check import check
from bes.enum_util.checked_int_enum import checked_int_enum

class requirement_hardness(checked_int_enum):
  # Requirement needed at runtime.  For example a dynamically linked library.
  RUN = 1

  # Requirement is tool needed at build time.  For example a compiler.
  TOOL = 2

  # Requirement needed only at build time.  For example a statically linked library.
  BUILD = 3
    
  # Requirement needed only for testing.
  TEST = 4
    
  DEFAULT = RUN

check.register_class(requirement_hardness,
                     include_seq = False,
                     cast_func = requirement_hardness.parse)
