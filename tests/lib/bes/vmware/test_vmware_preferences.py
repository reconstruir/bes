#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path
from bes.testing.unit_test import unit_test
from bes.fs.temp_file import temp_file

from bes.vmware.vmware_preferences import vmware_preferences as GP

class test_vmware_preferences(unit_test):

  def test_basic(self):
    content = '''\
.encoding = "UTF-8"
pref.dataCollectionEnabled = "FALSE"
pref.dataCollectionEnabled.epoch = ""
pref.keyboardAndMouse.maxProfiles = "4"
pref.keyboardAndMouse.vmHotKey.count = "0"
pref.keyboardAndMouse.vmHotKey.enabled = "FALSE"
pref.lastUpdateCheckSec = "1234567890"
'''
    prefs = GP(temp_file.make_temp_file(content = content))
    self.assertEqual( {
      '.encoding': 'UTF-8',
      'pref.dataCollectionEnabled': 'FALSE',
      'pref.dataCollectionEnabled.epoch': '',
      'pref.keyboardAndMouse.maxProfiles': '4',
      'pref.keyboardAndMouse.vmHotKey.count': '0',
      'pref.keyboardAndMouse.vmHotKey.enabled': 'FALSE',
      'pref.lastUpdateCheckSec': '1234567890',
    }, prefs.values )
###    g = GP(temp_file.make_temp_file(content = content))
###    self.assertEqual( {
###      '.encoding': 'UTF-8"
###pref.dataCollectionEnabled = "FALSE"
###pref.dataCollectionEnabled.epoch = ""
###pref.keyboardAndMoul( 'flintpass', c.password )
###    c = g.credentials('systemProp.vmware.wrapper')
###    self.assertEqual( 'tuser', c.username )
###    self.assertEqual( 'tpassword', c.password )
    
if __name__ == '__main__':
  unit_test.main()
