#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from unittest.mock import patch, MagicMock

from bes.testing.unit_test import unit_test
from bes.credentials.bf_password_resolver import bf_password_resolver as R
from bes.system.env_override import env_override

class test_bf_password_resolver(unit_test):

  def test_explicit_value(self):
    self.assertEqual('secret', R.resolve(value='secret'))

  def test_explicit_value_skips_env(self):
    with env_override({'MY_PASS': 'fromenv'}):
      self.assertEqual('explicit', R.resolve(value='explicit', env_var='MY_PASS'))

  def test_env_var_used(self):
    with env_override({'MY_PASS': 'fromenv'}):
      self.assertEqual('fromenv', R.resolve(env_var='MY_PASS', prompt=None))

  def test_env_var_missing_falls_through_to_prompt(self):
    with env_override({}):
      with patch('getpass.getpass', return_value='prompted') as mock_gp:
        result = R.resolve(env_var='NONEXISTENT_VAR_XYZ', prompt='Enter: ')
        self.assertEqual('prompted', result)
        mock_gp.assert_called_once_with('Enter: ')

  def test_keychain_used(self):
    mock_keyring = MagicMock()
    mock_keyring.get_password.return_value = 'fromkeychain'
    with patch.dict('sys.modules', {'keyring': mock_keyring}):
      with env_override({}):
        result = R.resolve(
          keychain_service = 'my.service',
          keychain_username = 'user',
          prompt = None,
        )
        self.assertEqual('fromkeychain', result)
        mock_keyring.get_password.assert_called_once_with('my.service', 'user')

  def test_keychain_import_error_falls_through(self):
    with patch.dict('sys.modules', {'keyring': None}):
      with env_override({}):
        with patch('getpass.getpass', return_value='prompted'):
          result = R.resolve(
            keychain_service = 'my.service',
            keychain_username = 'user',
            prompt = 'Enter: ',
          )
          self.assertEqual('prompted', result)

  def test_prompt_used_as_last_resort(self):
    with env_override({}):
      with patch('getpass.getpass', return_value='typed') as mock_gp:
        result = R.resolve(prompt='Vault: ')
        self.assertEqual('typed', result)
        mock_gp.assert_called_once_with('Vault: ')

  def test_prompt_none_skips_interactive(self):
    with env_override({}):
      with patch('getpass.getpass') as mock_gp:
        result = R.resolve(prompt=None)
        self.assertIsNone(result)
        mock_gp.assert_not_called()

  def test_require_true_raises(self):
    with env_override({}):
      with patch('getpass.getpass', return_value=''):
        with self.assertRaises(RuntimeError):
          R.resolve(prompt='Enter: ', require=True)

  def test_require_false_returns_none(self):
    with env_override({}):
      result = R.resolve(prompt=None, require=False)
      self.assertIsNone(result)

  def test_require_error_message_includes_env_var(self):
    with env_override({}):
      with patch('getpass.getpass', return_value=''):
        with self.assertRaises(RuntimeError) as ctx:
          R.resolve(env_var='BAT_VAULT_PASSWORD', prompt='Enter: ', require=True)
        self.assertIn('BAT_VAULT_PASSWORD', str(ctx.exception))

  def test_priority_env_beats_keychain(self):
    mock_keyring = MagicMock()
    mock_keyring.get_password.return_value = 'fromkeychain'
    with patch.dict('sys.modules', {'keyring': mock_keyring}):
      with env_override({'MY_PASS': 'fromenv'}):
        result = R.resolve(
          env_var = 'MY_PASS',
          keychain_service = 'my.service',
          keychain_username = 'user',
          prompt = None,
        )
        self.assertEqual('fromenv', result)
        mock_keyring.get_password.assert_not_called()

  def test_priority_keychain_beats_prompt(self):
    mock_keyring = MagicMock()
    mock_keyring.get_password.return_value = 'fromkeychain'
    with patch.dict('sys.modules', {'keyring': mock_keyring}):
      with env_override({}):
        with patch('getpass.getpass') as mock_gp:
          result = R.resolve(
            keychain_service = 'my.service',
            keychain_username = 'user',
            prompt = 'Enter: ',
          )
          self.assertEqual('fromkeychain', result)
          mock_gp.assert_not_called()

if __name__ == '__main__':
  unit_test.main()
