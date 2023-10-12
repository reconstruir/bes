#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from enum import IntFlag

class bc_ini_lexer_options(IntFlag):
  KEEP_QUOTES = 0x01
  ESCAPE_QUOTES = 0x02
  IGNORE_COMMENTS = 0x04
  DEFAULT_OPTIONS = 0x00
