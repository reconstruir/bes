#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

class bcli_missing_command_error(Exception):
  def __init__(self, message):
    super().__init__()
    self.message = message

  def __str__(self):
    return self.message
