#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from ..system.check import check
from bes.system.host_info import host_info
from bes.key_value.key_value_list import key_value_list
from bes.system.log import logger

from .bat_vmware_error import bat_vmware_error

class bat_vmware_system_info(object):
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

  _log = logger('bat_vmware_system_info')
  
  @classmethod
  def system_info(clazz, guest_os, guest_os_detailed_data):
    check.check_string(guest_os)
    check.check_string(guest_os_detailed_data)

    if guest_os_detailed_data:
      details = key_value_list.parse(guest_os_detailed_data).to_dict()
    else:
      details = {}
    clazz._log.log_d('system_info: guest_os="{}" details="{}"'.format(guest_os, details))
    if details:
      family_name = details.get('familyName', None)
      if not family_name:
        raise bat_vmware_error('Family name not found for guest os: "{}" - "{}"'.format(guest_os, details))
      return clazz._system_info_with_details(family_name, details)
    else:
      return clazz._system_info_without_details(guest_os)

  @classmethod
  def _system_info_with_details(clazz, family_name, details):
    assert family_name
    assert details

    family_name = family_name.lower()
    handler_name = '_system_info_{}'.format(family_name)
    handler = getattr(clazz, handler_name, None)
    if not handler:
      raise bat_vmware_error(f'Unknown guest os: "{family_name}" - "{details}"')
    result = handler(details)
    if not result:
      raise bat_vmware_error(f'Unknown guest os: "{family_name}" - "{details}"')
    return result

  @classmethod
  def _system_info_without_details(clazz, guest_os):
    return clazz._WITHOUT_DETAILS_TABLE.get(guest_os, None)
  
  @classmethod
  def _system_info_linux(clazz, details):
    arch = clazz._determine_arch(details)
    distro_name = details.get('distroName', None)
    assert distro_name
    distro_version = details.get('distroVersion', None)
    assert distro_version
    version_parts = distro_version.split('.')
    return host_info('linux', version_parts[0], version_parts[1], arch, distro_name.lower(), None, None)

  @classmethod
  def _system_info_windows(clazz, details):
    arch = clazz._determine_arch(details)
    distro_name = details.get('distroName', None)
    assert distro_name
    distro_version = details.get('distroVersion', None)
    assert distro_version
    version_parts = distro_version.split('.')
    return host_info('windows', version_parts[0], version_parts[1], arch, distro_name.lower(), None, None)

  @classmethod
  def _system_info_darwin(clazz, details):
    arch = clazz._determine_arch(details)
    distro_version = details.get('distroVersion', None)
    assert distro_version
    version_parts = distro_version.split('.')
    return host_info('macos', version_parts[0], version_parts[1], arch, '', None, None)
  
  @classmethod
  def _determine_arch(clazz, details):
    if details.get('bitness', None) == '64':
      arch = 'x86_64'
    else:
      arch = 'i386'
    return arch

  _WITHOUT_DETAILS_TABLE = {
    'windows9-64': host_info('windows', '10', '0', 'x86_64', '', None, None),
    'windows9': host_info('windows', '10', '0', 'i386', '', None, None),
  }
