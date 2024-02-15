#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os

from .btl_lexer_token import btl_lexer_token

class btl_parser_runtime_error(Exception):

  def __init__(self, token, context, message):
    super().__init__()
    self.token = token
    self.context = context
    self.message = message

  def __str__(self):
    position = self.context.position
    error_text = self.token.make_error_text(self.context.text, self.message)
    source_text = f'{self.context.source} line {position.line} column {position.column}'
    return f'{source_text}{os.linesep}{self.message}{os.linesep}{error_text}'
