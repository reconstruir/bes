# -*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

from ..system.check import check

from .vmware_vmx_file import vmware_vmx_file

class vmware_vm(namedtuple('vmware_vm', 'name, vm_id, vmx_filename')):
  'A class to represent a vmware vm.'
  
  def __new__(clazz, vm_id, vmx_filename):
    check.check_string(vm_id)
    check.check_string(vmx_filename)

    name = vmware_vmx_file(vmx_filename).nickname
    return clazz.__bases__[0].__new__(clazz,
                                      name,
                                      vm_id,
                                      vmx_filename)
check.register_class(vmware_vm)
