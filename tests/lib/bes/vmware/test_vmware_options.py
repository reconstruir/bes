#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test

from bes.vmware.vmware_options import vmware_options

class test_vmware_options(unit_test):

  def test_from_file(self):

    content = '''\
vmware
  vmrest_username: foo
  vmrest_password: sekret
  vmrest_port: 9999
  login_username: fred
  login_password: flintpass
'''
    tmp_config = self.make_temp_file(content = content)
    o = vmware_options.from_config_file(tmp_config)
    self.assertEqual( 'foo', o.vmrest_username )
    self.assertEqual( 'sekret', o.vmrest_password )
    self.assertEqual( 9999, o.vmrest_port )
    self.assertEqual( 'fred', o.login_username )
    self.assertEqual( 'flintpass', o.login_password )
    
if __name__ == '__main__':
  unit_test.main()
