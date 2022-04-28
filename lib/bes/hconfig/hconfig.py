#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import copy
import pprint

from bes.system.log import logger

from .hconfig_error import hconfig_error
from .hconfig_section import hconfig_section

_log = logger('hconfig')

class hconfig(hconfig_section):

  def __init__(self, d):
    _log.log_d(f'hconfig.__init__({pprint.pformat(d)})')
    super().__init__(copy.deepcopy(d), self, None)
    self._types = {}

  def register_caster(self, path, caster):
    check.check_string(path)
    check.check_hconfig_caster(caster)

    _types = super().__getattribute__('_types')
    if path in _types:
      raise hconfig_error(f'Caster already registered for path: {path}')
    _types[path] = caster
