#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test

from bes.vmware.vmware_vmx_file import vmware_vmx_file

class test_vmware_vmx_file(unit_test):

  def test_vmx_nickname(self):
    self.assertEqual( 'win10', vmware_vmx_file.nickname('/Users/foo/vms/win10.vmwarevm/win10.vmx') )
    
if __name__ == '__main__':
  unit_test.main()
