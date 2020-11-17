#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.macos.software_updater.software_updater import software_updater

class test_software_updater(unit_test):

  def test__parse_list_output(self):
    text = '''\
Software Update Tool

Finding available software
Software Update found the following new or updated software:
* Label: Command Line Tools for Xcode-12.2
	Title: Command Line Tools for Xcode, Version: 12.2, Size: 440907K, Recommended: YES,
* Label: Command Line Tools for Xcode-12.2
	Title: Command Line Tools for Xcode, Version: 12.2, Size: 440907K, Recommended: YES,
'''
    self.assertEqual( [
      ( 'Command Line Tools for Xcode',
        'Command Line Tools for Xcode-12.2',
        '12.2',
        '440907K',
        True,
       ) ,
    ], software_updater._parse_list_output(text) )
      
if __name__ == "__main__":
  unit_test.main()
