#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import getpass
import os
import socket
import tempfile

from bes.testing.unit_test import unit_test
from bes.testing.unit_test_class_skip import unit_test_class_skip
from bes.ssh.bssh_command import bssh_command
from bes.ssh.bssh_sandbox import bssh_sandbox

class test_bssh_sandbox(unit_test):

  _sandbox = None

  @classmethod
  def setUpClass(clazz):
    unit_test_class_skip.raise_skip_if_not_unix()
    unit_test_class_skip.raise_skip_if_not_has_command('sshd')
    unit_test_class_skip.raise_skip_if_not_has_command('ssh-keygen')
    clazz._sandbox = bssh_sandbox(strict_host_checking=False,
                                   allow_users=[getpass.getuser()])
    clazz._sandbox.start()

  @classmethod
  def tearDownClass(clazz):
    if clazz._sandbox:
      clazz._sandbox.stop()

  # 20
  def test_start_creates_sshd_dir(self):
    self.assertTrue(os.path.isdir(self._sandbox._sshd_dir))
    self.assertTrue(self._sandbox._sshd_dir.startswith(tempfile.gettempdir()))

  # 21
  def test_start_creates_client_dir(self):
    self.assertTrue(os.path.isdir(self._sandbox._client_dir))
    self.assertTrue(self._sandbox._client_dir.startswith(tempfile.gettempdir()))

  # 22
  def test_start_creates_key_pair(self):
    self.assertTrue(os.path.isfile(self._sandbox.key))
    self.assertTrue(os.path.isfile(self._sandbox.key + '.pub'))

  # 23
  def test_start_sshd_running(self):
    self.assertIsNotNone(self._sandbox._sshd_proc)
    self.assertIsNone(self._sandbox._sshd_proc.poll())

  # 24
  def test_sshd_accepts_connection(self):
    with socket.create_connection(('127.0.0.1', self._sandbox.port), timeout=2.0):
      pass  # connection succeeded

  # 25 — tested via tearDownClass; verify here by checking sshd is still running
  def test_stop_kills_sshd(self):
    s = bssh_sandbox(strict_host_checking=False, allow_users=[getpass.getuser()])
    s.start()
    proc = s._sshd_proc
    s.stop()
    self.assertIsNotNone(proc.poll())

  # 26
  def test_stop_removes_sshd_dir(self):
    s = bssh_sandbox(strict_host_checking=False, allow_users=[getpass.getuser()])
    s.start()
    d = s._sshd_dir
    s.stop()
    self.assertFalse(os.path.exists(d))

  # 27
  def test_stop_removes_client_dir(self):
    s = bssh_sandbox(strict_host_checking=False, allow_users=[getpass.getuser()])
    s.start()
    d = s._client_dir
    s.stop()
    self.assertFalse(os.path.exists(d))

  # 28
  def test_no_home_ssh_dir_written(self):
    ssh_dir = os.path.expanduser('~/.ssh')
    mtime_before = os.path.getmtime(ssh_dir) if os.path.exists(ssh_dir) else None
    s = bssh_sandbox(strict_host_checking=False, allow_users=[getpass.getuser()])
    s.start()
    s.stop()
    mtime_after = os.path.getmtime(ssh_dir) if os.path.exists(ssh_dir) else None
    self.assertEqual(mtime_before, mtime_after)

  # 29
  def test_nas_root_accessible_via_ssh(self):
    args = [
      '-i', self._sandbox.key,
      '-o', 'BatchMode=yes',
      '-o', 'StrictHostKeyChecking=no',
      '-o', f'UserKnownHostsFile={self._sandbox.known_hosts}',
      '-p', str(self._sandbox.port),
      '127.0.0.1',
      f'ls "{self._sandbox.nas_root}"',
    ]
    rv = bssh_command.call_command(args)
    self.assertEqual(0, rv.exit_code)

if __name__ == '__main__':
  unit_test.main()
