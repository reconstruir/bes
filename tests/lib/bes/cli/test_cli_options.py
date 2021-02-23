#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common.check import check
from bes.credentials.credentials import credentials
from bes.testing.unit_test import unit_test

from bes.cli.cli_options import cli_options

class _test_cli_options_error(Exception):
  def __init__(self, message, status_code = None):
    super(_test_cli_options_error, self).__init__()
    self.message = message
    self.status_code = status_code

  def __str__(self):
    return self.message

class _test_cli_options(cli_options):

  def __init__(self, **kargs):
    super(_test_cli_options, self).__init__(**kargs)

  @classmethod
  #@abstractmethod
  def default_values(clazz):
    'Return a dict of defaults for these options.'
    return {
      'verbose': False,
      'debug': False,
      'kiwi_username': None,
      'kiwi_password': None,
      'kiwi_port': None,
      'login_username': None,
      'login_password': None,
      'dont_ensure': False,
      'tty': None,
      'clone_vm': False,
      'vm_dir': None,
      'wait_programs_num_tries': 10,
      'wait_programs_sleep_time': 5.0,
    }
  
  @classmethod
  #@abstractmethod
  def sensitive_keys(clazz):
    'Return a tuple of keys that are secrets and should be protected from __str__.'
    return ( 'kiwi_password', 'login_password' )
  
  @classmethod
  #@abstractmethod
  def value_type_hints(clazz):
    return {
      'kiwi_port': int,
      'wait_programs_num_tries': int,
      'wait_programs_sleep_time': float,
    }

  @classmethod
  #@abstractmethod
  def config_file_key(clazz):
    return 'config_filename'

  @classmethod
  #@abstractmethod
  def config_file_section(clazz):
    return 'fruit'

  @classmethod
  #@abstractmethod
  def error_class(clazz):
    return _test_cli_options_error

  #@abstractmethod
  def check_value_types(self):
    'Check the type of each option.'
    check.check_bool(self.verbose)
    check.check_bool(self.debug)
    check.check_string(self.kiwi_username, allow_none = True)
    check.check_string(self.kiwi_password, allow_none = True)
    check.check_int(self.kiwi_port, allow_none = True)
    check.check_string(self.login_username, allow_none = True)
    check.check_string(self.login_password, allow_none = True)
    check.check_bool(self.dont_ensure)
    check.check_bool(self.dont_ensure)
    check.check_string(self.tty, allow_none = True)
    check.check_bool(self.clone_vm)
    check.check_string(self.vm_dir, allow_none = True)
    check.check_int(self.wait_programs_num_tries)
    check.check_float(self.wait_programs_sleep_time)
  
  @property
  def kiwi_credentials(self):
    if self.kiwi_username and not self.kiwi_password:
      raise _test_cli_options_error('both kiwi_username and kiwi_password need to be given.')
    if self.kiwi_password and not self.kiwi_username:
      raise _test_cli_options_error('both kiwi_password and kiwi_username need to be given.')
    if not self.kiwi_username:
      assert not self.kiwi_password
      return None
    return credentials('<cli>', username = self.kiwi_username, password = self.kiwi_password)

  @property
  def login_credentials(self):
    if self.login_username and not self.login_password:
      raise _test_cli_options_error('both login_username and login_password need to be given.')
    if self.login_password and not self.login_username:
      raise _test_cli_options_error('both login_password and login_username need to be given.')
    if not self.login_username:
      assert not self.login_password
      return None
    return credentials('<cli>', username = self.login_username, password = self.login_password)

class test_cli_options(unit_test):

  def xtest___init__(self):

    values = {
      'kiwi_username': 'foo',
      'kiwi_password': 'sekret',
      'kiwi_port': '9999',
      'login_username': 'fred',
      'login_password': 'flintpass',
    }
    o = _test_cli_options(**values)
    self.assertEqual( 'foo', o.kiwi_username )
    self.assertEqual( 'sekret', o.kiwi_password )
    self.assertEqual( 9999, o.kiwi_port )
    self.assertEqual( 'fred', o.login_username )
    self.assertEqual( 'flintpass', o.login_password )
  
  def test_from_config_file(self):

    content = '''\
fruit
  kiwi_username: foo
  kiwi_password: sekret
  kiwi_port: 9999
  login_username: fred
  login_password: flintpass
'''
    tmp_config = self.make_temp_file(content = content)
    o = _test_cli_options.from_config_file(tmp_config)
    self.assertEqual( 'foo', o.kiwi_username )
    self.assertEqual( 'sekret', o.kiwi_password )
    self.assertEqual( 9999, o.kiwi_port )
    self.assertEqual( 'fred', o.login_username )
    self.assertEqual( 'flintpass', o.login_password )

  def test_unknown_value_from_config_file(self):
    content = '''\
fruit
  kiwi_username: foo
  kiwi_password: sekret
  something_unknown: kiwi
'''
    tmp_config = self.make_temp_file(content = content)
    o = _test_cli_options.from_config_file(tmp_config)
    self.assertTrue( hasattr(o, 'kiwi_username') )
    self.assertTrue( hasattr(o, 'kiwi_password') )
    self.assertTrue( hasattr(o, 'kiwi_port') )
    self.assertFalse( hasattr(o, 'something_unknown') )
    
if __name__ == '__main__':
  unit_test.main()
