#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from .bfile_error import bfile_error

class bfile_permission_error(Exception):
  def __init__(self, message):
    super().__init__(message)
