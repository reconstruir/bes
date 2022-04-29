#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import copy
import pprint
import fnmatch

from ..system.log import logger
from ..system.check import check
from ..common.node import node

from .hconfig_error import hconfig_error
from .hconfig_path import hconfig_path
from .hconfig_section import hconfig_section

_log = logger('hconfig')

class hconfig(object):

  def __init__(self, d):
    _log.log_d(f'hconfig.__init__({pprint.pformat(d)})')
    self._section = hconfig_section(copy.deepcopy(d), self, None)
    self._types = node('root')

  def __getattr__(self, key):
    return getattr(self._section, key)
    
  def register_caster(self, path, caster):
    check.check_string(path)
    check.check_hconfig_caster(caster)

    hpath = hconfig_path(path, wildcards = True)
    if self._types.find_child_by_path_data(hpath.parts) != None:
      raise hconfig_error(f'Caster already registered for path: {path}')
    n = self._types.ensure_path(hpath.parts)
    setattr(n, '__bes_hconfig_caster__', caster)

  def find_caster(self, path):
    check.check_string(path)

    hpath = hconfig_path(path, wildcards = True)
    func = lambda n, part: fnmatch.fnmatch(part, n.data)
    n = self._types.find_child_by_path(hpath.parts, func)
    if n == None:
      return None
    assert hasattr(n, '__bes_hconfig_caster__')
    caster = getattr(n, '__bes_hconfig_caster__')
    return caster
