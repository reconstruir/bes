#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import hashlib
import os
import tempfile

from bes.testing.unit_test import unit_test
from bes.testing.unit_test_class_skip import unit_test_class_skip
from bes.openssl.bopenssl_command import bopenssl_command
from bes.openssl.bopenssl_digest import bopenssl_digest
from bes.openssl.bopenssl_error import bopenssl_error

class test_bopenssl_digest(unit_test):

  @classmethod
  def setUpClass(clazz):
    unit_test_class_skip.raise_skip_if_not_unix()
    unit_test_class_skip.raise_skip_if_not_has_command('openssl')

  # 33
  def test_sha256_known_value(self):
    content = b'hello file-sync'
    tmp = self.make_temp_file(content=content)
    expected = hashlib.sha256(content).hexdigest()
    self.assertEqual(expected, bopenssl_digest.sha256(tmp))

  # 34
  def test_sha256_empty_file(self):
    tmp = self.make_temp_file(content=b'')
    expected = hashlib.sha256(b'').hexdigest()
    self.assertEqual(expected, bopenssl_digest.sha256(tmp))

  # 35
  def test_sha256_file_in_temp_dir(self):
    tmp = self.make_temp_file(content=b'data')
    self.assertTrue(tmp.startswith(tempfile.gettempdir()))

  # 36
  def test_sha256_nonexistent_file_raises(self):
    with self.assertRaises(bopenssl_error):
      bopenssl_digest.sha256('/nonexistent/path/to/file.mp4')

  # 37
  def test_sha256_output_is_lowercase_hex(self):
    tmp = self.make_temp_file(content=b'test')
    result = bopenssl_digest.sha256(tmp)
    self.assertEqual(64, len(result))
    self.assertEqual(result, result.lower())
    self.assertTrue(all(c in '0123456789abcdef' for c in result))

  # 38
  def test_sha256_matches_hashlib(self):
    content = b'cross-check this'
    tmp = self.make_temp_file(content=content)
    expected = hashlib.sha256(content).hexdigest()
    self.assertEqual(expected, bopenssl_digest.sha256(tmp))

  # 39
  def test_sha512_crypt_produces_dollar6(self):
    unit_test_class_skip.raise_skip_if_not_has_command('openssl')
    result = bopenssl_digest.sha512_crypt('testpassword')
    self.assertTrue(result.startswith('$6$'), f'expected $6$... got: {result}')

  # 40
  def test_sha512_crypt_verifiable(self):
    # verify the hash round-trips using openssl itself
    password = 'verifyme'
    hashed = bopenssl_digest.sha512_crypt(password)
    # re-hash with the same salt (openssl passwd -6 -salt accepts the $6$salt$ prefix)
    salt = hashed.rsplit('$', 1)[0]  # e.g. $6$rounds=5000$saltsalt
    rv = bopenssl_command.call_command(
      ['passwd', '-6', '-stdin', '-salt', salt.split('$')[2]],
      input_data=(password + '\n').encode('utf-8'),
    )
    self.assertEqual(hashed, rv.stdout.strip())

if __name__ == '__main__':
  unit_test.main()
