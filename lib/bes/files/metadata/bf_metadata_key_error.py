#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from .bf_metadata_error import bf_metadata_error

class bf_metadata_key_error(bf_metadata_error):
  def __init__(self, message):
    super().__init__(message)
