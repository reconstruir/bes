#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.text import lexer_token, string_lexer
from bes.common import point

def TCOMMENT(s, x = 1, y = 1): return lexer_token(string_lexer.TOKEN_COMMENT, s, point(x, y))
def TDONE(x = 1, y = 1): return lexer_token(string_lexer.TOKEN_DONE, None, point(x, y))
def TSPACE(s = ' ', x = 1, y = 1): return lexer_token(string_lexer.TOKEN_SPACE, s, point(x, y))
def TSTRING(s, x = 1, y = 1): return lexer_token(string_lexer.TOKEN_STRING, s, point(x, y))
