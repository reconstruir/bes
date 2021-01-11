#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system.log import logger
from bes.common.check import check
from bes.credentials.credentials import credentials

from .vmware_client import vmware_client
from .vmware_credentials import vmware_credentials
from .vmware_error import vmware_error
from .vmware_server_controller import vmware_server_controller
from .vmware_util import vmware_util

class vmware_session(object):

  _log = logger('vmware_session')

  def __init__(self, port = None, credentials = None):
    check.check_int(port, allow_none = True)
    check.check_credentials(credentials, allow_none = True)

    if not credentials:
      credentials = vmware_credentials.make_random_credentials()

    self._log.log_d('vmware_session(port={} credentials={})'.format(port, credentials))
    self._port = port
    self._credentials = credentials

    vmware_credentials.set_credentials(credentials.username,
                                       credentials.password,
                                       num_tries = 100)
    self._server = None
    self._client = None

  def start(self):
    if self._server:
      return
    self._server = vmware_server_controller()
    self._server.start(port = self._port)
    self._client = vmware_client(address = self._server.address,
                                 auth = self._credentials)
    
  def stop(self):
    if not self._server:
      return
    self._client = None
    self._server.stop()
    self._server = None

  def call_client(self, method_name, *args, **kargs):
    check.check_string(method_name)

    if not self._client:
      raise vmware_error('session not started.  call start() first')
    func = getattr(self._client, method_name)
    return func(*args, **kargs)
