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

  @property
  def base_url(self):
    return 'http://{}:{}'.format(self._address[0], self._address[1])

  _vm = namedtuple('_vm', 'vm_id, path')
  def vms(self):
    'Return a list of vms'
    url = self._make_url('api/vms')

    headers = {
      'Accept': 'application/vnd.vmware.vmw.rest-v1+json',
    }
    
#curl 'http://localhost:8697/api/vms' -X GET --header 'Accept: application/vnd.vmware.vmw.rest-v1+json' -u"fred:FRED#1flint"
#    params = {
#      'q': 'name~"{}"'.format(ref_name),
#    }
#    params = params

#    $body = @{
#        'name' = $newvmname;
#        'parentId' = $sourcevmid
#    }

    self._log.log_d('url={} auth={} headers={}'.format(url, self._auth, headers))
    response = requests.get(url, auth = self._auth_tuple, headers = headers)
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
  
  def _make_url(self, fragment):
    check.check_string(fragment)

    return url_compat.urljoin(self.base_url, fragment)
