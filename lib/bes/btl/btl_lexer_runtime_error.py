#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os

class btl_lexer_runtime_error(Exception):

  def __init__(self, context, message):
    super().__init__()
    self.context = context
    self.message = message

  def __str__(self):
    position = self.context.position
    error_text = self.context.make_error_text(self.context.text, self.message)
    source_text = f'{self.context.source} line {position.line} column {position.column}'
    return f'{source_text}{os.linesep}{self.message}{os.linesep}{error_text}'
