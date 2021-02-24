#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common.check import check
from bes.system.host_info import host_info
from bes.key_value.key_value_list import key_value_list
from bes.system.log import logger

from .vmware_error import vmware_error

class vmware_system_info(object):
  '''
  Class to map vmware vmx file guestOS and guestOS.detailed.data to bes.system.host_info
  The possible list of values for vmware vmx file guestOS is not very well documented.
  Some people have reversed engineered it as best they could.  For example:
    https://joefitzgerald.tumblr.com/post/70320581729/vmware-fusion-vmx-guestos-values/amp
    http://sanbarrow.com/vmx/vmx-guestos.html
    https://vdc-download.vmware.com/vmwb-repository/dcr-public/da47f910-60ac-438b-8b9b-6122f4d14524/16b7274a-bf8b-4b4c-a05e-746f2aa93c8c/doc/vim.vm.GuestOsDescriptor.GuestOsIdentifier.html

  But none of these are up to date.  The mappings below are limited to the operating systems
  that I was dealing with when I wrote this code and not exhaustive.  However it should
  be possible to expand the mapping as needed.
  '''

  _log = logger('vmware_system_info')
  
  @classmethod
  def system_info(clazz, guest_os, guest_os_detailed_data):
    check.check_string(guest_os)
    check.check_string(guest_os_detailed_data)

    if guest_os_detailed_data:
      details = key_value_list.parse(guest_os_detailed_data)
    else:
      details = {}

    clazz._log.log_d('system_info: guest_os="{}" details="{}"'.format(guest_os, details))

    result = clazz._TABLE.get(guest_os, None)
    if not result:
      raise RuntimeError('Unknown guest os: "{}" - "{}"'.format(guest_os, details))
    
    return result

  _TABLE = {
    'darwin18-64': host_info('macos', '10', '14', 'x86_64', '', None),
    'darwin19-64': host_info('macos', '10', '15', 'x86_64', '', None),
    'darwin20-64': host_info('macos', '10', '16', 'x86_64', '', None),
  }
