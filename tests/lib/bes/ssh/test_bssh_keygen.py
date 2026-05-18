#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os
import stat
import tempfile

from bes.testing.unit_test import unit_test
from bes.testing.unit_test_class_skip import unit_test_class_skip
from bes.ssh.bssh_keygen import bssh_keygen
from bes.ssh.bssh_error import bssh_error

class test_bssh_keygen(unit_test):

  @classmethod
  def setUpClass(clazz):
    unit_test_class_skip.raise_skip_if_not_unix()
    unit_test_class_skip.raise_skip_if_not_has_command('ssh-keygen')

  # 5
  def test_generate_ed25519_creates_private_key(self):
    tmp_dir = self.make_temp_dir()
    key_path = os.path.join(tmp_dir, 'id_ed25519')
    bssh_keygen.generate_ed25519(key_path)
    self.assertTrue(os.path.isfile(key_path))

  # 6
  def test_generate_ed25519_creates_public_key(self):
    tmp_dir = self.make_temp_dir()
    key_path = os.path.join(tmp_dir, 'id_ed25519')
    bssh_keygen.generate_ed25519(key_path)
    self.assertTrue(os.path.isfile(key_path + '.pub'))

  # 7
  def test_generate_ed25519_private_key_not_in_home(self):
    tmp_dir = self.make_temp_dir()
    key_path = os.path.join(tmp_dir, 'id_ed25519')
    bssh_keygen.generate_ed25519(key_path)
    self.assertTrue(key_path.startswith(tempfile.gettempdir()))

  # 8
  def test_key_type_in_public_key(self):
    tmp_dir = self.make_temp_dir()
    key_path = os.path.join(tmp_dir, 'id_ed25519')
    bssh_keygen.generate_ed25519(key_path)
    with open(key_path + '.pub') as f:
      pub = f.read()
    self.assertTrue(pub.startswith('ssh-ed25519 '))

  # 9
  def test_comment_in_public_key(self):
    tmp_dir = self.make_temp_dir()
    key_path = os.path.join(tmp_dir, 'id_ed25519')
    bssh_keygen.generate_ed25519(key_path, comment='test-comment')
    with open(key_path + '.pub') as f:
      pub = f.read()
    self.assertIn('test-comment', pub)

  # 10
  def test_key_permissions(self):
    tmp_dir = self.make_temp_dir()
    key_path = os.path.join(tmp_dir, 'id_ed25519')
    bssh_keygen.generate_ed25519(key_path)
    mode = os.stat(key_path).st_mode & 0o777
    self.assertEqual(0o600, mode)

  # 11
  def test_overwrite_existing_raises(self):
    tmp_dir = self.make_temp_dir()
    key_path = os.path.join(tmp_dir, 'id_ed25519')
    bssh_keygen.generate_ed25519(key_path)
    with self.assertRaises(bssh_error):
      bssh_keygen.generate_ed25519(key_path)

if __name__ == '__main__':
  unit_test.main()
