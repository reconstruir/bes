#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

class btl_parser_runtime_error(Exception):
  def __init__(self, message = None):
    super().__init__()

    self.message = message

  def __str__(self):
    return self.message or ''
