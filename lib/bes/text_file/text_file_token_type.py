#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common.check import check
from bes.enum_util.checked_enum import checked_enum

class text_file_token_type(checked_enum):
  COMMENT = 'comment'
  COMMENT_DELIMITER = 'comment_delimiter'
  SPACE = 'space'
  TEXT = 'text'

check.register_class(text_file_token_type,
                     include_seq = False,
                     cast_func = text_file_token_type.parse)
