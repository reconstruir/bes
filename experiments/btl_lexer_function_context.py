#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from ..system.check import check

class btl_lexer_function_context(object):

  def __init__(self, lexer, lexer_context, tokens, char):
    check.check_btl_lexer(lexer)
    check.check_btl_lexer_context(context)
    check.check_btl_lexer_token_list(tokens)
    check.check_string(char)
    
    self.lexer = lexer
    self.lexer_context = lexer_context
    self.tokens = tokens
    self.char = char
