#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system.log import logger
from bes.common.check import check
from bes.credentials.credentials import credentials

from .vmware_client import vmware_client
from .vmware_credentials import vmware_credentials
from .vmware_error import vmware_error
from .vmware_server_controller import vmware_server_controller

class vmware_session(object):

  _log = logger('vmware_session')

  def __init__(self, port = None, credentials = None):
    check.check_int(port, allow_none = True)
    check.check_credentials(credentials, allow_none = True)

    if not credentials:
      credentials = vmware_credentials.make_random_credentials()

    self._log.log_d('vmware_session(port={} credentials={})'.format(port, credentials))

    vmware_credentials.set_credentials(clazz, credentials.username, credentials.password)
    self._server = vmware_server_controller(port = port)
    self._server.start()
    self._address = self._server.address()
    self._client = vmware_server(port = port, auth = self._address)
