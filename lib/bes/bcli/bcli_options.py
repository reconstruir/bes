 #-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple
from bes.system.check import check
from bes.system.log import logger

from .bcli_options_desc import bcli_options_desc

class bcli_options(object):

  _log = logger('bcli_options')
  
  def __init__(self, desc, **kwargs):
    self._desc = check.check_bcli_options_desc(desc)

  @property
  def desc(self):
    return self._desc

  def __getattr__(self, name):
    self._log.log_method_d()
    return 42

  def __setattr__(self, name, value):
    self._log.log_method_d()

check.register_class(bcli_options, include_seq = False)
