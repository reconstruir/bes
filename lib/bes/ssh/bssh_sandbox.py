#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import getpass
import os
import os.path as path
import socket
import stat
import subprocess
import tempfile
import time

from .bssh_error import bssh_error
from .bssh_keygen import bssh_keygen
from .bssh_sandbox_error import bssh_sandbox_error

class bssh_sandbox(object):
  '''
  Starts a real sshd on 127.0.0.1 for integration tests.
  All files go into two temp dirs — no writes to ~/.ssh or any fixed path.

  Usage:
    sandbox = bssh_sandbox()
    sandbox.start()
    # sandbox.host, sandbox.port, sandbox.key, sandbox.client_dir, sandbox.nas_root
    sandbox.stop()

  For tests pass strict_host_checking=False and allow_users=[getpass.getuser()].
  Production code never constructs bssh_sandbox.
  '''

  def __init__(self, strict_host_checking=True, allow_users=None):
    self._strict_host_checking = strict_host_checking
    self._allow_users = allow_users or []
    self._sshd_dir = None
    self._client_dir = None
    self._sshd_proc = None
    self.host = '127.0.0.1'
    self.port = None
    self.key = None
    self.client_dir = None
    self.nas_root = None

  def start(self):
    self._sshd_dir = tempfile.mkdtemp(prefix='bssh_sandbox_sshd_')
    self._client_dir = tempfile.mkdtemp(prefix='bssh_sandbox_client_')
    self.client_dir = self._client_dir
    self.nas_root = path.join(self._sshd_dir, 'nas')
    os.makedirs(self.nas_root)

    # generate host key
    host_key_path = path.join(self._sshd_dir, 'host_key')
    bssh_keygen.generate_ed25519(host_key_path, comment='sandbox-host')

    # generate client key pair in client dir
    client_key_path = path.join(self._client_dir, 'id_ed25519')
    bssh_keygen.generate_ed25519(client_key_path, comment='sandbox-client')
    self.key = client_key_path

    # authorized_keys
    pub_key_path = client_key_path + '.pub'
    authorized_keys_path = path.join(self._sshd_dir, 'authorized_keys')
    with open(pub_key_path, 'r') as f:
      pub_key = f.read()
    with open(authorized_keys_path, 'w') as f:
      f.write(pub_key)
    os.chmod(authorized_keys_path, stat.S_IRUSR | stat.S_IWUSR)

    known_hosts_path = path.join(self._client_dir, 'known_hosts')
    self.known_hosts = known_hosts_path

    # pick a free port
    self.port = self._find_free_port()

    # write sshd_config
    sshd_config_path = path.join(self._sshd_dir, 'sshd_config')
    pid_file = path.join(self._sshd_dir, 'sshd.pid')
    config_lines = [
      f'ListenAddress {self.host}',
      f'Port {self.port}',
      f'AuthorizedKeysFile {authorized_keys_path}',
      f'HostKey {host_key_path}',
      'PasswordAuthentication no',
      'ChallengeResponseAuthentication no',
      'UsePAM no',
      'Subsystem sftp internal-sftp',
      f'PidFile {pid_file}',
    ]
    if self._allow_users:
      config_lines.append('AllowUsers ' + ' '.join(self._allow_users))
    if not self._strict_host_checking:
      config_lines.append('StrictModes no')
    with open(sshd_config_path, 'w') as f:
      f.write('\n'.join(config_lines) + '\n')

    # start sshd
    sshd_exe = self._find_sshd()
    try:
      self._sshd_proc = subprocess.Popen(
        [sshd_exe, '-D', '-e', '-f', sshd_config_path],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
      )
    except OSError as ex:
      raise bssh_sandbox_error(f'failed to start sshd: {ex}')

    self._wait_for_port(timeout=10.0)
    self._write_known_hosts(known_hosts_path, host_key_path + '.pub')

  def stop(self):
    if self._sshd_proc is not None:
      self._sshd_proc.terminate()
      try:
        self._sshd_proc.wait(timeout=5.0)
      except subprocess.TimeoutExpired:
        self._sshd_proc.kill()
      self._sshd_proc = None
    self._rm_tree(self._sshd_dir)
    self._rm_tree(self._client_dir)
    self._sshd_dir = None
    self._client_dir = None

  def make_executor(self):
    'Return a bssh_executor configured to talk to this sandbox.'
    from .bssh_executor import bssh_executor
    return bssh_executor(
      self.key,
      f'{self.host}:{self.port}' if self.port != 22 else self.host,
      known_hosts_file=self.known_hosts,
      strict_host_checking=self._strict_host_checking,
    )

  @staticmethod
  def _find_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
      s.bind(('127.0.0.1', 0))
      return s.getsockname()[1]

  @staticmethod
  def _find_sshd():
    for candidate in ('/usr/sbin/sshd', '/usr/bin/sshd', '/usr/local/sbin/sshd'):
      if path.exists(candidate):
        return candidate
    raise bssh_sandbox_error('sshd not found')

  def _write_known_hosts(self, known_hosts_path, host_pub_key_path):
    with open(host_pub_key_path, 'r') as f:
      pub_key_line = f.read().strip()
    key_parts = pub_key_line.split(maxsplit=2)
    # known_hosts format for a non-default port: [host]:port key-type key-data
    entry = f'[{self.host}]:{self.port} {key_parts[0]} {key_parts[1]}\n'
    with open(known_hosts_path, 'w') as f:
      f.write(entry)

  def _wait_for_port(self, timeout=10.0):
    deadline = time.time() + timeout
    while time.time() < deadline:
      try:
        with socket.create_connection(('127.0.0.1', self.port), timeout=0.5):
          return
      except OSError:
        time.sleep(0.1)
    raise bssh_sandbox_error(f'sshd did not start on port {self.port} within {timeout}s')

  @staticmethod
  def _rm_tree(d):
    if d is None or not path.exists(d):
      return
    import shutil
    shutil.rmtree(d, ignore_errors=True)
