#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system.log import logger
from ..system.check import check
from bes.credentials.credentials import credentials

from .bat_vmware_client import bat_vmware_client
from .vmware_credentials import vmware_credentials
from .vmware_error import vmware_error
from .vmware_server_controller import vmware_server_controller
from .vmware_util import vmware_util

class vmware_session(object):

  _log = logger('vmware_session')

  def __init__(self, port = None, credentials = None):
    check.check_int(port, allow_none = True)
    check.check_credentials(credentials, allow_none = True)

    self._log.log_d('vmware_session() port={} credentials={}'.format(port, credentials))

    if not credentials or not credentials.username :
      self._log.log_d('vmware_session() using random credentials={}'.format(credentials))
      credentials = vmware_credentials.make_random_credentials()
      vmware_credentials.set_credentials(credentials.username,
                                         credentials.password,
                                         num_tries = 100)
    self._port = port
    self._credentials = credentials

    self.server = None
    self.client = None

  def start(self):
    self._log.log_d('start')
    if self.server:
      self._log.log_d('server already exists')
      return
    self._log.log_d('creating server')
    self.server = vmware_server_controller()
    self._log.log_d('starting server on port {}'.format(self._port))
    self.server.start(port = self._port)
    self._log.log_d('starting client with address {}'.format(self.server.address))
    self.client = bat_vmware_client(address = self.server.address,
                                auth = self._credentials)
    self._log.log_d('client started')
    
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

  def resolve_vm_id(self, name, raise_error = True):
    vm_id = self.call_client('vm_name_to_id', name)
    if not vm_id and raise_error:
      raise vmware_error('failed to resolve vm id: "{}"'.format(name))
    return vm_id

  def ensure_vm_running(self, vm_id):
    return self.call_client('vm_set_power', vm_id, 'on', wait = 'ssh')
