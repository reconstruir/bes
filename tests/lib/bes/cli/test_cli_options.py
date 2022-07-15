#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.cli.cli_options import cli_options
from bes.system.check import check
from bes.credentials.credentials import credentials
from bes.system.env_override import env_override
from bes.testing.unit_test import unit_test

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
      'username': None,
      'password': None,
      'port': None,
      'num_tries': 10,
      'sleep_time': 5.0,
    }
  
  @classmethod
  #@abstractmethod
  def sensitive_keys(clazz):
    'Return a tuple of keys that are secrets and should be protected from __str__.'
    return ( 'password', )
  
  @classmethod
  #@abstractmethod
  def value_type_hints(clazz):
    return {
      'port': int,
      'num_tries': int,
      'sleep_time': float,
    }

  @classmethod
  #@abstractmethod
  def config_file_key(clazz):
    return 'config_filename'

  @classmethod
  #@abstractmethod
  def config_file_env_var_name(clazz):
    return '_BES_CLI_OPTIONS_UNIT_TEST_CONFIG_FILE'
  
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
    check.check_string(self.username, allow_none = True)
    check.check_string(self.password, allow_none = True)
    check.check_int(self.port, allow_none = True)
    check.check_int(self.num_tries)
    check.check_float(self.sleep_time)
  
  @property
  def credentials(self):
    if self.username and not self.password:
      raise _test_cli_options_error('both username and password need to be given.')
    if self.password and not self.username:
      raise _test_cli_options_error('both password and username need to be given.')
    if not self.username:
      assert not self.password
      return None
    return credentials('<cli>', username = self.username, password = self.password)

class _test_cli_options_subclass(_test_cli_options):

  def __init__(self, **kargs):
    super(_test_cli_options_subclass, self).__init__(**kargs)

  @classmethod
  #@abstractmethod
  def default_values(clazz):
    'Return a dict of defaults for these options.'
    return clazz.super_default_values({
      'sub_can_do': True,
      'sub_fruit': 'kiwi',
      'sub_username': None,
      'sub_password': None,
    })
  
  @classmethod
  #@abstractmethod
  def sensitive_keys(clazz):
    'Return a tuple of keys that are secrets and should be protected from __str__.'
    return clazz.super_sensitive_keys(( 'sub_password', ))
  
  @classmethod
  #@abstractmethod
  def value_type_hints(clazz):
    return clazz.super_value_type_hints({
      'sub_can_do': bool,
      'sub_fruit': str,
      'sub_username': str,
      'sub_password': str,
    })

  @classmethod
  #@abstractmethod
  def config_file_key(clazz):
    return super(_test_cli_options_subclass, clazz).config_file_key()

  @classmethod
  #@abstractmethod
  def config_file_env_var_name(clazz):
    return '_BES_CLI_OPTIONS_UNIT_TEST_CONFIG_FILE_SUBCLASS'
  
  @classmethod
  #@abstractmethod
  def config_file_section(clazz):
    return super(_test_cli_options_subclass, clazz).config_file_section()

  #@abstractmethod
  def check_value_types(self):
    'Check the type of each option.'
    super(_test_cli_options_subclass, self).check_value_types()
    check.check_bool(self.sub_can_do)
    check.check_string(self.sub_fruit)
    check.check_string(self.sub_username, allow_none = True)
    check.check_string(self.sub_password, allow_none = True)
  
  @property
  def sub_credentials(self):
    if self.sub_username and not self.sub_password:
      raise _test_cli_options_error('both sub_username and sub_password need to be given.')
    if self.sub_password and not self.sub_username:
      raise _test_cli_options_error('both sub_password and sub_username need to be given.')
    if not self.sub_username:
      assert not self.sub_password
      return None
    return credentials('<cli>', username = self.sub_username, password = self.sub_password)
  
class test_cli_options(unit_test):

  def test___init__(self):
    values = {
      'username': 'foo',
      'password': 'sekret',
      'port': 9999,
    }
    o = _test_cli_options(**values)
    self.assertEqual( 'foo', o.username )
    self.assertEqual( 'sekret', o.password )
    self.assertEqual( 9999, o.port )
    self.assertEqual( {
      'debug': False,
      'num_tries': 10,
      'password': 'sekret',
      'port': 9999,
      'sleep_time': 5.0,
      'username': 'foo',
      'verbose': False,
    }, o.__dict__ )

  def test___init__with_type_hints(self):
    values = {
      'username': 'foo',
      'password': 'sekret',
      'port': '9999',
    }
    o = _test_cli_options(**values)
    self.assertEqual( 'foo', o.username )
    self.assertEqual( 'sekret', o.password )
    self.assertEqual( 9999, o.port )
    self.assertEqual( {
      'debug': False,
      'num_tries': 10,
      'password': 'sekret',
      'port': 9999,
      'sleep_time': 5.0,
      'username': 'foo',
      'verbose': False,
    }, o.__dict__ )

  def test___init___unknown_value(self):
    values = {
      'username': 'foo',
      'password': 'sekret',
      'port': 9999,
      'something_unknown': 'kiwi',
    }
    o = _test_cli_options(**values)
    self.assertEqual( 'foo', o.username )
    self.assertEqual( 'sekret', o.password )
    self.assertEqual( 9999, o.port )
    self.assertEqual( {
      'debug': False,
      'num_tries': 10,
      'password': 'sekret',
      'port': 9999,
      'sleep_time': 5.0,
      'username': 'foo',
      'verbose': False,
    }, o.__dict__ )
    
  def test_from_config_file(self):
    content = '''\
fruit
  username: foo
  password: sekret
  port: 9999
'''
    tmp_config = self.make_temp_file(content = content)
    o = _test_cli_options.from_config_file(tmp_config)
    self.assertEqual( 'foo', o.username )
    self.assertEqual( 'sekret', o.password )
    self.assertEqual( 9999, o.port )

  def test_from_config_file_from_env(self):
    content = '''\
fruit
  username: foo
  password: sekret
  port: 9999
'''
    tmp_config = self.make_temp_file(content = content)
    with env_override( { '_BES_CLI_OPTIONS_UNIT_TEST_CONFIG_FILE': tmp_config }) as env:
      o = _test_cli_options()
      self.assertEqual( 'foo', o.username )
      self.assertEqual( 'sekret', o.password )
      self.assertEqual( 9999, o.port )
    
  def test_unknown_value_from_config_file(self):
    content = '''\
fruit
  username: foo
  password: sekret
  something_unknown: kiwi
'''
    tmp_config = self.make_temp_file(content = content)
    o = _test_cli_options.from_config_file(tmp_config)
    self.assertTrue( hasattr(o, 'username') )
    self.assertTrue( hasattr(o, 'password') )
    self.assertTrue( hasattr(o, 'port') )
    self.assertFalse( hasattr(o, 'something_unknown') )

class test_cli_options_subclass(unit_test):

  def test___init__(self):
    values = {
      'username': 'foo',
      'password': 'sekret',
      'port': 9999,
      'sub_can_do': False,
      'sub_fruit': 'papaya',
      'sub_username': 'fred',
      'sub_password': 'flintpass',
    }
    o = _test_cli_options_subclass(**values)
    self.assertEqual( 'foo', o.username )
    self.assertEqual( 'sekret', o.password )
    self.assertEqual( 9999, o.port )
    self.assertEqual( False, o.sub_can_do )
    self.assertEqual( 'papaya', o.sub_fruit )
    self.assertEqual( 'fred', o.sub_username )
    self.assertEqual( 'flintpass', o.sub_password )
    self.assertEqual( {
      'debug': False,
      'num_tries': 10,
      'password': 'sekret',
      'port': 9999,
      'sleep_time': 5.0,
      'username': 'foo',
      'verbose': False,
      'sub_can_do': False,
      'sub_fruit': 'papaya',
      'sub_username': 'fred',
      'sub_password': 'flintpass',
    }, o.__dict__ )

  def xtest___init__with_type_hints(self):
    values = {
      'username': 'foo',
      'password': 'sekret',
      'port': '9999', # string but value type is int
      'sub_can_do': 'False', # string but value type is bool
      'sub_fruit': 'papaya',
      'sub_username': 'fred',
      'sub_password': 'flintpass',
    }
    o = _test_cli_options_subclass(**values)
    self.assertEqual( 'foo', o.username )
    self.assertEqual( 'sekret', o.password )
    self.assertEqual( 9999, o.port )
    self.assertEqual( False, o.sub_can_do )
    self.assertEqual( 'papaya', o.sub_fruit )
    self.assertEqual( 'fred', o.sub_username )
    self.assertEqual( 'flintpass', o.sub_password )
    self.assertEqual( {
      'debug': False,
      'num_tries': 10,
      'password': 'sekret',
      'port': 9999,
      'sleep_time': 5.0,
      'username': 'foo',
      'verbose': False,
      'sub_can_do': False,
      'sub_fruit': 'papaya',
      'sub_username': 'fred',
      'sub_password': 'flintpass',
    }, o.__dict__ )

  def xtest___init___unknown_value(self):
    values = {
      'username': 'foo',
      'password': 'sekret',
      'port': 9999,
      'something_unknown': 'kiwi',
    }
    o = _test_cli_options_subclass(**values)
    self.assertEqual( 'foo', o.username )
    self.assertEqual( 'sekret', o.password )
    self.assertEqual( 9999, o.port )
    self.assertEqual( {
      'debug': False,
      'num_tries': 10,
      'password': 'sekret',
      'port': 9999,
      'sleep_time': 5.0,
      'username': 'foo',
      'verbose': False,
      'sub_can_do': True,
      'sub_fruit': 'kiwi',
      'sub_username': None,
      'sub_password': None,
    }, o.__dict__ )
    
  def xtest_from_config_file(self):
    content = '''\
fruit
  username: foo
  password: sekret
  port: 9999
'''
    tmp_config = self.make_temp_file(content = content)
    o = _test_cli_options.from_config_file(tmp_config)
    self.assertEqual( 'foo', o.username )
    self.assertEqual( 'sekret', o.password )
    self.assertEqual( 9999, o.port )

  def xtest_from_config_file_from_env(self):
    content = '''\
fruit
  username: foo
  password: sekret
  port: 9999
'''
    tmp_config = self.make_temp_file(content = content)
    with env_override( { '_BES_CLI_OPTIONS_UNIT_TEST_CONFIG_FILE_SUBCLASS': tmp_config }) as env:
      o = _test_cli_options_subclass()
      self.assertEqual( 'foo', o.username )
      self.assertEqual( 'sekret', o.password )
      self.assertEqual( 9999, o.port )
    
  def xtest_unknown_value_from_config_file(self):
    content = '''\
fruit
  username: foo
  password: sekret
  something_unknown: kiwi
'''
    tmp_config = self.make_temp_file(content = content)
    o = _test_cli_options.from_config_file(tmp_config)
    self.assertTrue( hasattr(o, 'username') )
    self.assertTrue( hasattr(o, 'password') )
    self.assertTrue( hasattr(o, 'port') )
    self.assertFalse( hasattr(o, 'something_unknown') )
    
if __name__ == '__main__':
  unit_test.main()
