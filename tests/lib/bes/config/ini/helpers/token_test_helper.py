#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.config.ini.bc_ini_lexer_token import bc_ini_lexer_token
from bes.config.ini.bc_ini_lexer import bc_ini_lexer
from bes.common.point import point

def TCOMMENT(s, x = 1, y = 1): return bc_ini_lexer_token(bc_ini_lexer.TOKEN_COMMENT, s, point(x, y))
def TDONE(x = 1, y = 1): return bc_ini_lexer_token(bc_ini_lexer.TOKEN_DONE, None, point(x, y))
def TSPACE(s = ' ', x = 1, y = 1): return bc_ini_lexer_token(bc_ini_lexer.TOKEN_SPACE, s, point(x, y))
def TSTRING(s, x = 1, y = 1): return bc_ini_lexer_token(bc_ini_lexer.TOKEN_STRING, s, point(x, y))
