#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import copy
import pprint
import fnmatch

from ..compat.StringIO import StringIO
from ..system.log import logger
from ..system.check import check
from ..common.node import node

from .hconfig_error import hconfig_error
from .hconfig_path import hconfig_path
from .hconfig_section import hconfig_section
from .hconfig_type_base import hconfig_type_base

_log = logger('hconfig')

class hconfig(object):

  def __init__(self, d):
    _log.log_d(f'hconfig.__init__({pprint.pformat(d)})')
    #self._section = hconfig_section(copy.deepcopy(d), self, None)
    self._section = hconfig_section(d, self, None)
    self._types = node('root')

  def __str__(self):
    buf = StringIO()
    buf.write(str(self._section))
    return buf.getvalue()
    
  def __getattr__(self, key):
    return getattr(self._section, key)

  def to_dict(self):
    return self._section.to_dict()
  
  def register_type(self, path, caster):
    check.check_string(path)
    if not issubclass(caster, hconfig_type_base):
      raise TypeError(f'caster should be a subclass of hconfig_type_base: {caster}')

    hpath = hconfig_path(path, wildcards = True)
    if self._types.find_child_by_path_data(hpath.parts) != None:
      raise hconfig_error(f'Caster already registered for path: {path}')
    n = self._types.ensure_path(hpath.parts)
    setattr(n, '__bes_hconfig_type__', caster)

  def find_caster(self, path):
    check.check_string(path)

    hpath = hconfig_path(path, wildcards = True)
    func = lambda n, part: fnmatch.fnmatch(part, n.data)
    n = self._types.find_child_by_path(hpath.parts, func)
    if n == None:
      return None
#    print(f'n={n}')
#    assert hasattr(n, '__bes_hconfig_type__')
    caster = getattr(n, '__bes_hconfig_type__', None)
    if caster == None:
      return None
    return caster
