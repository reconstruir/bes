#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import pprint
import requests
import time

from ..system.check import check
from bes.compat import url_compat
from bes.net_util.port_probe import port_probe
from bes.system.log import logger
from bes.common.json_util import json_util

from .bat_vmware_error import bat_vmware_error
from .bat_vmware_shared_folder import bat_vmware_shared_folder
from .bat_vmware_shared_folder import bat_vmware_shared_folder_list
from .bat_vmware_vm import bat_vmware_vm

class bat_vmware_client(object):
  '''
  A class to deal with the vmware fusion/workstation rest api
  fusion: https://code.vmware.com/apis/1044

  workstation pro: https://code.vmware.com/apis/1043
  
  '''
  
  _log = logger('bat_vmware_client')
  
  def __init__(self, address, auth):
    check.check_tuple(address)
    check.check_credentials(auth)
    
    self._address = address
    self._auth = auth
    self._headers = {
      'Accept': 'application/vnd.vmware.vmw.rest-v1+json',
      'Content-Type': 'application/vnd.vmware.vmw.rest-v1+json',
    }

  @property
  def base_url(self):
    return 'http://{}:{}/api/'.format(self._address[0], self._address[1])

  def _check_response_401(self, response):
    if response.status_code == 401:
      raise bat_vmware_error('401 authentication error for "{}"  Check vmrest_username and vmrest_password.'.format(response.url))
    return False

  def _check_response(self, response):
    self._check_response_401(response)
    
  def vms(self):
    'Return a list of vms'
    url = self._make_url('vms')
    response = self._make_request('get', url)
    self._check_response(response)

    if response.status_code != 200:
      raise bat_vmware_error('Error querying: "{}": {}'.format(url, response.status_code))
    response_data = response.json()
    self._log.log_d('vms: response_data={}'.format(pprint.pformat(response_data)))
    result = []
    for item in response_data:
      vm = bat_vmware_vm(item['id'], item['path'])
      result.append(vm)
    return result

  def vm_settings(self, vm_id):
    'Return a settings for a vm'
    check.check_string(vm_id)
    
    url = self._make_url('vms/{}'.format(vm_id))
    response = self._make_request('get', url)
    if response.status_code != 200:
      raise bat_vmware_error('Error querying: "{}": {}'.format(url, response.status_code))
    response_data = response.json()
    self._log.log_d('vms: response_data={}'.format(pprint.pformat(response_data)))
    return response_data

  def vm_config(self, vm_id, key):
    'Return a config for a vm'
    check.check_string(vm_id)
    check.check_string(key)
    
    url = self._make_url('vms/{}/params/{}'.format(vm_id, key))
    response = self._make_request('get', url)
    if response.status_code != 200:
      raise bat_vmware_error('Error querying: "{}": {}'.format(url, response.status_code))
    response_data = response.json()
    self._log.log_d('vms: response_data={}'.format(pprint.pformat(response_data)))
    name = response_data.get('name', None)
    if not name:
      raise bat_vmware_error('Invalid response_data: {}'.format(pprint.pformat(response_data)))
    value = response_data.get('value', None)
    if not value:
      raise bat_vmware_error('Invalid response_data: {}'.format(pprint.pformat(response_data)))
    if name == key:
      return value
    raise bat_vmware_error('Config value "{}" not found'.format(key))

  def vm_get_mac_address(self, vm_id):
    'Return the mac address for a vm'
    check.check_string(vm_id)

    try:
      return self.vm_config(vm_id, 'ethernet0.address')
    except bat_vmware_error as ex:
      pass
    try:
      return self.vm_config(vm_id, 'ethernet0.generatedAddress')
    except bat_vmware_error as ex:
      pass
    return None
  
  def vm_get_power(self, vm_id):
    'Return power status for a vm.'
    check.check_string(vm_id)
    
    url = self._make_url('vms/{}/power'.format(vm_id))
    response = self._make_request('get', url)
    if response.status_code != 200:
      raise bat_vmware_error('Error querying: "{}": {}'.format(url, response.status_code))
    response_data = response.json()
    self._log.log_d('vms: response_data={}'.format(pprint.pformat(response_data)))
    power_state = response_data.get('power_state', None)
    if not power_state:
      raise bat_vmware_error('Invalid response_data: {}'.format(pprint.pformat(response_data)))
    return power_state == 'poweredOn'

  POWER_STATES = ( 'on', 'off', 'shutdown', 'suspend', 'pause', 'unpause' )
  def vm_set_power(self, vm_id, state, wait = None):
    'Return power status for a vm.'
    check.check_string(vm_id)
    check.check_string(state)
    check.check_string(wait, allow_none = True)

    if state not in self.POWER_STATES:
      raise bat_vmware_error('Invalid power stte "{}" - Should be one of: {}'.format(state,
                                                                                 ' '.join(self.POWER_STATES)))
    
    url = self._make_url('vms/{}/power'.format(vm_id))

    data = state
    response = self._make_request('put', url, data = data)
    if response.status_code != 200:
      raise bat_vmware_error('Error querying: "{}": {}'.format(url, response.status_code))
    response_data = response.json()
    self._log.log_d('vm_power: response_data={}'.format(pprint.pformat(response_data)))
    power_state = response_data.get('power_state', None)
    if not power_state:
      raise bat_vmware_error('Invalid response_data: {}'.format(pprint.pformat(response_data)))
    result = power_state == 'poweredOn'

    if result:
      if wait in [ 'ip', 'ssh' ]:
        ip_address = self._wait_for_ip_address(vm_id)
      if wait in [ 'ssh' ]:
        self._wait_for_ssh(ip_address)
          
    return result

  # FIXME: add timeout or max retries
  def _wait_for_ip_address(self, vm_id):
    ip_address = None
    while True:
      try:
        ip_address = self.vm_get_ip_address(vm_id)
        break
      except bat_vmware_error as ex:
        self._log.log_d('vm_power: caught exception waiting for ip address: {}'.format(ex))
        time.sleep(1.0)
    return ip_address

  def _wait_for_ssh(self, ip_address):
    ssh_port = ( ip_address, 22 )
    while True:
      try:
        if port_probe.is_open(ssh_port):
          break
      except bat_vmware_error as ex:
        self._log.log_d('vm_power: caught exception waiting for ssh port: {}'.format(ex))
        time.sleep(1.0)
        
  def request(self, endpoint, params):
    'Return power status for a vm.'
    check.check_string(endpoint)
    check.check_dict(params, check.STRING_TYPES, check.STRING_TYPES, allow_none = True)

    if not endpoint.startswith(self.base_url):
      endpoint = self.base_url + endpoint
    
    response = self._make_request('get', endpoint)
    if response.status_code != 200:
      raise bat_vmware_error('Error querying: "{}": {}'.format(endpoint, response.status_code))
    response_data = response.json()
    self._log.log_d('request: response_data={}'.format(pprint.pformat(response_data)))
    return response_data

  def vm_get_ip_address(self, vm_id):
    'Return a config for a vm'
    check.check_string(vm_id)
    
    url = self._make_url('vms/{}/ip'.format(vm_id))
    response = self._make_request('get', url)
    if response.status_code != 200:
      raise bat_vmware_error('Error querying: "{}": {}'.format(url, response.status_code))
    response_data = response.json()
    self._log.log_d('vms: response_data={}'.format(pprint.pformat(response_data)))
    ip_address = response_data.get('ip', None)
    if not ip_address:
      raise bat_vmware_error('Invalid response_data: {}'.format(pprint.pformat(response_data)))
    return ip_address

  def vm_name_to_id(self, name):
    'Return the id for a vm name'
    check.check_string(name)

    vms = self.vms()
    for vm in vms:
      if name in [ vm.name, vm.vm_id, vm.vmx_filename ]:
        return vm.vm_id
    return None
  
  def _make_request(self, method, url, params = None, json = None, data = None):
    auth = self._auth.to_tuple('username', 'password')
    func = getattr(requests, method)
    self._log.log_d('_make_request() method={} url={} params={} json={} data={}'.format(method,
                                                                                        url,
                                                                                        params,
                                                                                        json,
                                                                                        data))

    response = func(url,
                    data = data,
                    json = json,
                    params = params,
                    auth = auth,
                    headers = self._headers)
    self._log.log_d('_make_request() response: status_code={} url={} headers={} content={}'.format(response.status_code,
                                                                                                   response.url,
                                                                                                   response.headers,
                                                                                                   response.content))
    return response
  
  def _make_url(self, fragment):
    check.check_string(fragment)

    return url_compat.urljoin(self.base_url, fragment)

  def call_client(self, method_name, *args, **kargs):
    check.check_string(method_name)
    func = getattr(self, method_name)
    return func(*args, **kargs)
  
#    params = {
#      'q': 'name~"{}"'.format(ref_name),
#    }
#    params = params

#    $body = @{
#        'name' = $newvmname;
#        'parentId' = $sourcevmid
#    }

  def vm_get_shared_folders(self, vm_id):
    'Return a list of shared folders for a vm'
    check.check_string(vm_id)
    
    url = self._make_url('vms/{}/sharedfolders'.format(vm_id))
    response = self._make_request('get', url)
    if response.status_code != 200:
      raise bat_vmware_error('Error querying: "{}": {}'.format(url, response.status_code))
    response_data = response.json()
    self._log.log_d('vm_get_shared_folders: response_data={}'.format(pprint.pformat(response_data)))
    result = bat_vmware_shared_folder_list()
    for item in response_data:
      vm = bat_vmware_shared_folder(item['folder_id'], item['host_path'], item['flags'])
      result.append(vm)
    return result

  def vm_update_shared_folder(self, vm_id, folder_id, host_path, flags):
    check.check_string(vm_id)
    check.check_string(folder_id)
    check.check_string(host_path)
    check.check_int(flags)

    url = self._make_url('vms/{}/sharedfolders/{}'.format(vm_id, folder_id))

    json = {
      'host_path': host_path,
      'flags': flags,
    }
    response = self._make_request('put', url, json = json) #data = data)
    if response.status_code != 200:
      raise bat_vmware_error('Error querying: "{}": {}'.format(url, response.status_code))
    response_data = response.json()
    self._log.log_d('vm_set_shared_folders: response_data={}'.format(pprint.pformat(response_data)))
    result = []
    for item in response_data:
      vm = bat_vmware_shared_folder(item['folder_id'], item['host_path'], item['flags'])
      result.append(vm)
    return result

  def vm_add_shared_folder(self, vm_id, folder_id, host_path, flags):
    check.check_string(vm_id)
    check.check_string(folder_id)
    check.check_string(host_path)
    check.check_int(flags)

    folder = bat_vmware_shared_folder(folder_id, host_path, flags)
    url = self._make_url('vms/{}/sharedfolders'.format(vm_id))
    json = folder.to_json()
    response = self._make_request('post', url, data = json)
    if response.status_code == 409:
      raise bat_vmware_error('shared folder already exists: "{}"'.format(folder_id))
    elif response.status_code != 201:
      raise bat_vmware_error('Error querying: "{}": {}'.format(url, response.status_code))
    response_data = response.json()
    self._log.log_d('vm_add_shared_folder: response_data={}'.format(pprint.pformat(response_data)))
    result = bat_vmware_shared_folder_list()
    for item in response_data:
      vm = bat_vmware_shared_folder(item['folder_id'], item['host_path'], item['flags'])
      result.append(vm)
    return result

  def vm_delete_shared_folder(self, vm_id, folder_id):
    check.check_string(vm_id)
    check.check_string(folder_id)

    url = self._make_url('vms/{}/sharedfolders/{}'.format(vm_id, folder_id))
    response = self._make_request('delete', url)
    if response.status_code != 204:
      raise bat_vmware_error('Error deleting: "{}": {}\n{}'.format(url, response.status_code, response.content))

  def vm_copy(self, vm_id, new_vm_id):
    check.check_string(vm_id)
    check.check_string(new_vm_id)

    url = self._make_url('vms')
    data = {
      'name': new_vm_id,
      'parentId': vm_id,
    }
    json = json_util.to_json(data, indent = 2, sort_keys = True)
    response = self._make_request('post', url, data = json)
    response_data = response.json()

    if response.status_code == 409:
      if response_data['Code'] == 107:
        raise bat_vmware_error('{} - {}'.format(response_data['Code'], response_data['Message']))
      else:
        raise bat_vmware_error('vm already exists: "{}"'.format(new_vm_id))
    elif response.status_code != 201:
      raise bat_vmware_error('Error querying: "{}": {}'.format(url, response.status_code))
    response_data = response.json()
    self._log.log_d('vm_copy: response_data={}'.format(pprint.pformat(response_data)))
    return response_data

  def vm_delete(self, vm_id, force_shutdown):
    check.check_string(vm_id)
    check.check_bool(force_shutdown)

    self._log.log_d('vm_delete: vm_id={} force_shutdown={}'.format(vm_id, force_shutdown))
    
    if force_shutdown:
      self._log.log_d('vm_delete: shutting vm down first.')
      self.vm_set_power(vm_id, 'off')
      
    url = self._make_url('vms/{}'.format(vm_id))
    response = self._make_request('delete', url)

    if response.status_code != 204:
      raise bat_vmware_error('Error deleting: "{}": {}'.format(url, response.status_code))

check.register_class(bat_vmware_client, include_seq = False)
