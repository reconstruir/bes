#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import pprint
import requests
import sys
import time

from collections import namedtuple

from bes.compat import url_compat
from bes.common.check import check
from bes.system.log import logger

from .vmware_error import vmware_error

class vmware_client_api(object):
  'A class to deal with the vmware fusion rest api'
  
  _log = logger('vmware_client_api')
  
  def __init__(self, address, auth):
    check.check_tuple(address)
    check.check_credentials(auth)
    
    self._address = address
    self._auth = auth
    self._auth_tuple = ( self._auth.username, self._auth.password )
    self._headers = {
      'Accept': 'application/vnd.vmware.vmw.rest-v1+json',
      'Content-Type': 'application/vnd.vmware.vmw.rest-v1+json',
    }

  @property
  def base_url(self):
    return 'http://{}:{}/api/'.format(self._address[0], self._address[1])

  _vm = namedtuple('_vm', 'vm_id, path')
  def vms(self):
    'Return a list of vms'
    url = self._make_url('vms')
    response = self._make_request('get', url)
    if response.status_code != 200:
      raise vmware_error('Error querying: "{}": {}'.format(url, response.status_code))
    response_data = response.json()
    self._log.log_d('vms: response_data={}'.format(pprint.pformat(response_data)))
    result = []
    for item in response_data:
      result.append(self._vm(item['id'], item['path']))
    return result

  _vmx = namedtuple('_vm', 'vm_id, path')
  def vm_settings(self, vm_id):
    'Return a settings for a vm'
    check.check_string(vm_id)
    
    url = self._make_url('vms/{}'.format(vm_id))
    response = self._make_request('get', url)
    if response.status_code != 200:
      raise vmware_error('Error querying: "{}": {}'.format(url, response.status_code))
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
      raise vmware_error('Error querying: "{}": {}'.format(url, response.status_code))
    response_data = response.json()
    self._log.log_d('vms: response_data={}'.format(pprint.pformat(response_data)))
    name = response_data.get('name', None)
    if not name:
      raise vmware_error('Invalid response_data: {}'.format(pprint.pformat(response_data)))
    value = response_data.get('value', None)
    if not value:
      raise vmware_error('Invalid response_data: {}'.format(pprint.pformat(response_data)))
    if name == key:
      return value
    raise vmware_error('Config value "{}" not found'.format(key))

  def vm_get_mac_address(self, vm_id):
    'Return the mac address for a vm'
    check.check_string(vm_id)

    return self.vm_config(vm_id, 'ethernet0.generatedAddress')
  
  def vm_get_power(self, vm_id):
    'Return power status for a vm.'
    check.check_string(vm_id)
    
    url = self._make_url('vms/{}/power'.format(vm_id))
    response = self._make_request('get', url)
    if response.status_code != 200:
      raise vmware_error('Error querying: "{}": {}'.format(url, response.status_code))
    response_data = response.json()
    self._log.log_d('vms: response_data={}'.format(pprint.pformat(response_data)))
    power_state = response_data.get('power_state', None)
    if not power_state:
      raise vmware_error('Invalid response_data: {}'.format(pprint.pformat(response_data)))
    return power_state == 'poweredOn'

  def vm_set_power(self, vm_id, state):
    'Return power status for a vm.'
    check.check_string(vm_id)
    check.check_string(state)
    
    url = self._make_url('vms/{}/power'.format(vm_id))

    data = state
    response = self._make_request('put', url, data = data)
    if response.status_code != 200:
      raise vmware_error('Error querying: "{}": {}'.format(url, response.status_code))
    response_data = response.json()
    self._log.log_d('vms: response_data={}'.format(pprint.pformat(response_data)))
    power_state = response_data.get('power_state', None)
    if not power_state:
      raise vmware_error('Invalid response_data: {}'.format(pprint.pformat(response_data)))
    return power_state == 'poweredOn'

  def request(self, endpoint, params):
    'Return power status for a vm.'
    check.check_string(endpoint)
    check.check_dict(params, check.STRING_TYPES, check.STRING_TYPES, allow_none = True)

    if not endpoint.startswith(self.base_url):
      endpoint = self.base_url + endpoint
    
    response = self._make_request('get', endpoint)
    if response.status_code != 200:
      raise vmware_error('Error querying: "{}": {}'.format(endpoint, response.status_code))
    response_data = response.json()
    self._log.log_d('request: response_data={}'.format(pprint.pformat(response_data)))
    return response_data
  
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

#    params = {
#      'q': 'name~"{}"'.format(ref_name),
#    }
#    params = params

#    $body = @{
#        'name' = $newvmname;
#        'parentId' = $sourcevmid
#    }

  
