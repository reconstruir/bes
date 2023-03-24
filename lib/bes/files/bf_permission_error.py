#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from .bf_error import bf_error

class bf_permission_error(Exception):
  def __init__(self, message):
    super().__init__(message)
