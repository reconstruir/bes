#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test

from bes.bat_vmware.bat_vmware_options import bat_vmware_options

class test_bat_vmware_options(unit_test):

  def test___init__(self):
    values = {
      'vmrest_username': 'foo',
      'vmrest_password': 'sekret',
      'vmrest_port': '9999',
      'login_username': 'fred',
      'login_password': 'flintpass',
    }
    o = bat_vmware_options(**values)
    self.assertEqual( 'foo', o.vmrest_username )
    self.assertEqual( 'sekret', o.vmrest_password )
    self.assertEqual( 9999, o.vmrest_port )
    self.assertEqual( 'fred', o.login_username )
    self.assertEqual( 'flintpass', o.login_password )

  def test___init___with_type_hints(self):
    values = {
      'vmrest_username': 'foo',
      'vmrest_password': 'sekret',
      'vmrest_port': 9999,
      'login_username': 'fred',
      'login_password': 'flintpass',
    }
    o = bat_vmware_options(**values)
    self.assertEqual( 'foo', o.vmrest_username )
    self.assertEqual( 'sekret', o.vmrest_password )
    self.assertEqual( 9999, o.vmrest_port )
    self.assertEqual( 'fred', o.login_username )
    self.assertEqual( 'flintpass', o.login_password )

  def test___init___with_unknown_value(self):
    values = {
      'vmrest_username': 'foo',
      'vmrest_password': 'sekret',
      'vmrest_port': 9999,
      'login_username': 'fred',
      'login_password': 'flintpass',
      'something_unknown': 'kiwi',
    }
    o = bat_vmware_options(**values)
    self.assertEqual( 'foo', o.vmrest_username )
    self.assertEqual( 'sekret', o.vmrest_password )
    self.assertEqual( 9999, o.vmrest_port )
    self.assertEqual( 'fred', o.login_username )
    self.assertEqual( 'flintpass', o.login_password )
    self.assertFalse( hasattr(o, 'something_unknown') )
    
  def test_from_config_file(self):

    content = '''\
vmware
  vmrest_username: foo
  vmrest_password: sekret
  vmrest_port: 9999
  login_username: fred
  login_password: flintpass
'''
    tmp_config = self.make_temp_file(content = content)
    o = bat_vmware_options.from_config_file(tmp_config)
    self.assertEqual( 'foo', o.vmrest_username )
    self.assertEqual( 'sekret', o.vmrest_password )
    self.assertEqual( 9999, o.vmrest_port )
    self.assertEqual( 'fred', o.login_username )
    self.assertEqual( 'flintpass', o.login_password )

  def test_unknown_value_from_config_file(self):
    content = '''\
vmware
  vmrest_username: foo
  vmrest_password: sekret
  something_unknown: kiwi
'''
    tmp_config = self.make_temp_file(content = content)
    o = bat_vmware_options.from_config_file(tmp_config)
    self.assertTrue( hasattr(o, 'vmrest_username') )
    self.assertTrue( hasattr(o, 'vmrest_password') )
    self.assertTrue( hasattr(o, 'vmrest_port') )
    self.assertFalse( hasattr(o, 'something_unknown') )
    
if __name__ == '__main__':
  unit_test.main()
