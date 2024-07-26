#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from .bcli_type_manager import bcli_type_manager

class bcli_global_type_manager(object):

  _instance = bcli_type_manager()

  def __new__(cls, *args, **kwargs):
    return cls._instance

  def __call__(self, *args, **kwargs):
    return self._instance(*args, **kwargs)
