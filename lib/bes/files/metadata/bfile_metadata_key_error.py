#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from .bfile_metadata_error import bfile_metadata_error

class bfile_metadata_key_error(bfile_metadata_error):
  def __init__(self, message):
    super().__init__(message)