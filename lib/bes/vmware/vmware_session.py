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
    self.server = None
    self.client = None

  def start(self):
    if self.server:
      return
    self.server = vmware_server_controller()
    self.server.start(port = self._port)
    self.client = vmware_client(address = self.server.address,
                                auth = self._credentials)
    
  def stop(self):
    if not self.server:
      return
    self.client = None
    self.server.stop()
    self.server = None

  def call_client(self, method_name, *args, **kargs):
    check.check_string(method_name)

    if not self.client:
      raise vmware_error('session not started.  call start() first')
    func = getattr(self.client, method_name)
    return func(*args, **kargs)

  def resolve_vm_id(self, name):
    return self.call_client('vm_name_to_id', name)

  def ensure_vm_running(self, vm_id):
    return self.call_client('vm_set_power', vm_id, 'on', wait = 'ssh')
