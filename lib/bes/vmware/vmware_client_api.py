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
    }

  @property
  def base_url(self):
    return 'http://{}:{}'.format(self._address[0], self._address[1])

  _vm = namedtuple('_vm', 'vm_id, path')
  def vms(self):
    'Return a list of vms'
    url = self._make_url('api/vms')

#    params = {
#      'q': 'name~"{}"'.format(ref_name),
#    }
#    params = params

#    $body = @{
#        'name' = $newvmname;
#        'parentId' = $sourcevmid
#    }

    self._log.log_d('url={} auth={} headers={}'.format(url,
                                                       self._auth,
                                                       self._headers))
    response = requests.get(url,
                            auth = self._auth_tuple,
                            headers = self._headers)
    self._log.log_d('vms: response={} url={} headers={}'.format(response,
                                                                response.url,
                                                                response.headers))
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
    
    url = self._make_url('api/vms/{}'.format(vm_id))

    self._log.log_d('vm_settings: url={} auth={} headers={}'.format(url,
                                                                    self._auth,
                                                                    self._headers))
    response = requests.get(url,
                            auth = self._auth_tuple,
                            headers = self._headers)
    self._log.log_d('vm_settings: response={} url={} headers={}'.format(response,
                                                                        response.url,
                                                                        response.headers))
    if response.status_code != 200:
      raise vmware_error('Error querying: "{}": {}'.format(url, response.status_code))
    response_data = response.json()
    self._log.log_d('vms: response_data={}'.format(pprint.pformat(response_data)))
    return response_data
  
  def _make_url(self, fragment):
    check.check_string(fragment)

    return url_compat.urljoin(self.base_url, fragment)
