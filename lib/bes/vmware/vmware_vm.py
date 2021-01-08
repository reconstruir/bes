# -*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

from bes.common.check import check
from bes.common.string_util import string_util
from bes.property.cached_property import cached_property

class vmware_vm(namedtuple('vmware_vm', 'vm_id, path, name')):
  'A class to represent a vmware vm.'
  
  def __new__(clazz, vm_id, path):
    check.check_string(vm_id)
    check.check_string(path)

    return clazz.__bases__[0].__new__(clazz, vm_id, path, clazz._make_name(path))

  @classmethod
  def _make_name(clazz, path):
    'Return a short revision'
    i = path.rfind('/')
    if i < 0:
      return None
    vmx = path[i + 1:]
    return string_util.remove_tail(vmx, '.vmx')
