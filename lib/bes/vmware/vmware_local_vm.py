#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from bes.system.log import logger
from bes.common.check import check
from bes.fs.file_find import file_find
from bes.property.cached_property import cached_property

from .vmware_error import vmware_error
from .vmware_preferences import vmware_preferences
from .vmware_vmx import vmware_vmx

class vmware_local_vm(object):

  logger = logger('vmware_local_vm')
  
  def __init__(self, vmx_filename):
    self.vmx_filename = path.abspath(vmx_filename)
    self.vmx_config = vmware_preferences(self.vmx_filename)

  def __str__(self):
    return self.vmx_filename

  def __repr__(self):
    return self.vmx_filename
  
  @cached_property
  def nickname(self):
    return vmware_vmx.vmx_filename_nickname(self.vmx_filename)

  @cached_property
  def uuid(self):
    return self.vmx_config.get_value('uuid.bios')
