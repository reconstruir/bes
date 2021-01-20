# -*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

from bes.common.check import check

from .vmware_vmx import vmware_vmx

class vmware_vm(namedtuple('vmware_vm', 'name, vm_id, path')):
  'A class to represent a vmware vm.'
  
  def __new__(clazz, vm_id, path):
    check.check_string(vm_id)
    check.check_string(path)

    return clazz.__bases__[0].__new__(clazz, vmware_vmx.nickname(path), vm_id, path)
