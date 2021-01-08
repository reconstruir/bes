#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import pprint, requests, sys, time

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
    print(address)
    self._address = address
    self._auth = auth

  @property
  def base_url(self):
    return 'http://{}:{}'.format(self._address[0], self._address[1])

  def vms(self):
    'Return a list of vms'
    url = self._make_url('api/vms')

    headers = {
      'Accept': 'application/vnd.vmware.vmw.rest-v1+json',
    }
    
#curl 'http://localhost:8697/api/vms' -X GET --header 'Accept: application/vnd.vmware.vmw.rest-v1+json' -u"fred:FRED#1flint"

    auth = ( self._auth.username, self._auth.password )
    self._log.log_d('url={} auth={} headers={}'.format(url, auth, headers))
    response = requests.get(url, auth = auth, headers = headers)
    print(response)
    print(response.content)
    return []
  
  def _make_url(self, fragment):
    check.check_string(fragment)

    return url_compat.urljoin(self.base_url, fragment)
