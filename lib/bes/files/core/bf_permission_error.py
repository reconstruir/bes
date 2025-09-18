#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

class bf_permission_error(Exception):
  def __init__(self, message = None):
    super().__init__(message)

  def __str__(self):
    return self.message or ''
