#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test

from bes.vmware.vmware_vmx import vmware_vmx

class test_vmware_vmx(unit_test):

  def test_vmx_filename_nickname(self):
    self.assertEqual( 'win10', vmware_vmx.vmx_filename_nickname('/Users/foo/vms/win10.vmwarevm/win10.vmx') )
    
if __name__ == '__main__':
  unit_test.main()
