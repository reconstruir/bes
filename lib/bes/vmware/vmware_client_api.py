#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import pprint, requests, sys, time

from collections import namedtuple

from bes.compat import url_compat
from bes.common.check import check
from bes.system.log import logger

from .vmware_error import vmware_error

class vmware_client_api(object):
  'A class to deal with the vmware fusion rest api'
  
  _log = logger('vmware_server_api')
  
  def __init__(self, address, auth):
    check.check_tuple(address)
    check.check_credentials(auth)

    self._address = address
    self._auth = auth

  @property
  def base_url(self):
    return 'http://{}:{}'.format(self._address[0], self._address[1])

  def vms(self):
    'Return a list of vms'
    url = self._make_url('vms')
    response = requests.get(url)
    print(response)
    print(response.content)
  
  @classmethod
  def _make_url(clazz, fragment):
    check.check_string(fragment)

    return url_compat.urljoin(base_url, api_fragment)
