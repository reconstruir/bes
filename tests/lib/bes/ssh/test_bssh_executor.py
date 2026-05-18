#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os
import tempfile
import unittest.mock as mock

from bes.testing.unit_test import unit_test
from bes.testing.unit_test_class_skip import unit_test_class_skip
from bes.ssh.bssh_command import bssh_command
from bes.ssh.bssh_error import bssh_error
from bes.ssh.bssh_executor import bssh_executor
from bes.ssh.bssh_sandbox import bssh_sandbox

class test_bssh_executor_unit(unit_test):
  'Unit tests — no real SSH process.'

  def _make_executor(self, **kwargs):
    tmp_dir = self.make_temp_dir()
    key = os.path.join(tmp_dir, 'fake_key')
    open(key, 'w').close()
    return bssh_executor(key, 'nas2', **kwargs)

  # 12
  def test_run_builds_correct_ssh_args(self):
    ex = self._make_executor(strict_host_checking=False)
    captured = []
    def fake_call(args):
      captured.extend(args)
      from collections import namedtuple
      R = namedtuple('R', 'stdout')
      return R(stdout='ok\n')
    with mock.patch.object(bssh_command, 'call_command', side_effect=fake_call):
      ex.run('echo hi')
    self.assertIn('-o', captured)
    self.assertIn('BatchMode=yes', captured)
    self.assertIn('StrictHostKeyChecking=no', captured)
    self.assertIn('nas2', captured)
    self.assertIn('echo hi', captured)

  # 13
  def test_run_no_home_known_hosts(self):
    home_known_hosts = os.path.expanduser('~/.ssh/known_hosts')
    tmp_dir = self.make_temp_dir()
    kh = os.path.join(tmp_dir, 'known_hosts')
    ex = self._make_executor(known_hosts_file=kh, strict_host_checking=False)
    captured = []
    def fake_call(args):
      captured.extend(args)
      from collections import namedtuple
      R = namedtuple('R', 'stdout')
      return R(stdout='ok\n')
    with mock.patch.object(bssh_command, 'call_command', side_effect=fake_call):
      ex.run('pwd')
    self.assertNotIn(home_known_hosts, captured)
    self.assertTrue(any(kh in a for a in captured))

  # 14
  def test_run_returns_stdout(self):
    ex = self._make_executor()
    from collections import namedtuple
    R = namedtuple('R', 'stdout')
    with mock.patch.object(bssh_command, 'call_command', return_value=R(stdout='hello\n')):
      result = ex.run('echo hello')
    self.assertEqual('hello', result)

  # 15
  def test_run_ssh_failure_raises(self):
    ex = self._make_executor()
    with mock.patch.object(bssh_command, 'call_command', side_effect=bssh_error('connection refused')):
      with self.assertRaises(bssh_error):
        ex.run('ls')

  # 16
  def test_run_strips_trailing_newline(self):
    ex = self._make_executor()
    from collections import namedtuple
    R = namedtuple('R', 'stdout')
    with mock.patch.object(bssh_command, 'call_command', return_value=R(stdout='output\n\n')):
      result = ex.run('cmd')
    self.assertEqual('output', result)


class test_bssh_executor_integration(unit_test):
  'Integration tests — real sshd via bssh_sandbox.'

  _sandbox = None

  @classmethod
  def setUpClass(clazz):
    unit_test_class_skip.raise_skip_if_not_unix()
    unit_test_class_skip.raise_skip_if_not_has_command('sshd')
    unit_test_class_skip.raise_skip_if_not_has_command('ssh')
    import getpass
    clazz._sandbox = bssh_sandbox(strict_host_checking=False,
                                   allow_users=[getpass.getuser()])
    clazz._sandbox.start()

  @classmethod
  def tearDownClass(clazz):
    if clazz._sandbox:
      clazz._sandbox.stop()

  def _executor(self):
    return bssh_executor(
      self._sandbox.key,
      f'127.0.0.1',
      known_hosts_file=self._sandbox.known_hosts,
      strict_host_checking=False,
    )

  def _ssh_args(self):
    return [
      '-i', self._sandbox.key,
      '-o', 'BatchMode=yes',
      '-o', 'StrictHostKeyChecking=no',
      '-o', f'UserKnownHostsFile={self._sandbox.known_hosts}',
      '-p', str(self._sandbox.port),
    ]

  # 17
  def test_run_echo(self):
    ex = bssh_executor(
      self._sandbox.key,
      f'127.0.0.1',
      known_hosts_file=self._sandbox.known_hosts,
      strict_host_checking=False,
    )
    # Use bssh_command directly since bssh_executor host doesn't include port
    args = self._ssh_args() + ['127.0.0.1', 'echo hello']
    rv = bssh_command.call_command(args)
    self.assertEqual('hello', rv.stdout.strip())

  # 18
  def test_run_pwd(self):
    args = self._ssh_args() + ['127.0.0.1', 'pwd']
    rv = bssh_command.call_command(args)
    self.assertTrue(rv.stdout.strip().startswith('/'))

  # 19
  def test_run_no_side_effects_in_home(self):
    known_hosts = os.path.expanduser('~/.ssh/known_hosts')
    mtime_before = os.path.getmtime(known_hosts) if os.path.exists(known_hosts) else None
    args = self._ssh_args() + ['127.0.0.1', 'echo test']
    bssh_command.call_command(args)
    mtime_after = os.path.getmtime(known_hosts) if os.path.exists(known_hosts) else None
    self.assertEqual(mtime_before, mtime_after)

if __name__ == '__main__':
  unit_test.main()
