#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.macos.softwareupdater.softwareupdater import softwareupdater

class test_softwareupdater(unit_test):

  def test__parse_list_output_catalina_format(self):
    text = '''\
Software Update Tool

Finding available software
Software Update found the following new or updated software:
* Label: Command Line Tools for Xcode-12.2
\tTitle: Command Line Tools for Xcode, Version: 12.2, Size: 440907K, Recommended: YES, 
'''
    self.assertEqual( [
      ( 'Command Line Tools for Xcode-12.2',
        'Command Line Tools for Xcode',
        { 'version': '12.2', 'size': '440907K', 'recommended': True },
       ) ,
    ], softwareupdater._parse_list_output(text) )
  
  def test__parse_list_output_dups(self):
    text = '''\
Software Update Tool

Finding available software
Software Update found the following new or updated software:
* Label: Command Line Tools for Xcode-12.2
\tTitle: Command Line Tools for Xcode, Version: 12.2, Size: 440907K, Recommended: YES,
* Label: Command Line Tools for Xcode-12.2
\tTitle: Command Line Tools for Xcode, Version: 12.2, Size: 440907K, Recommended: YES,
'''
    self.assertEqual( [
      ( 'Command Line Tools for Xcode-12.2',
        'Command Line Tools for Xcode',
        { 'version': '12.2', 'size': '440907K', 'recommended': True },
       ) ,
    ], softwareupdater._parse_list_output(text) )

  def test__parse_list_output_no_updates(self):
    text = '''\
Software Update Tool

Finding available software
No new software available.
'''
    self.assertEqual( [], softwareupdater._parse_list_output(text) )

  def test__parse_list_output_mojave_format(self):
    text = '''\
Software Update Tool

Finding available software
Software Update found the following new or updated software:
   * Safari14.0.1MojaveAuto-14.0.1
\tSafari (14.0.1), 67518K [recommended]
   * Security Update 2020-005-10.14.6
\tSecurity Update 2020-005 (10.14.6), 1633218K [recommended] [restart]
   * Safari14.0MojaveAuto-10.14.6
\tmacOS Supplemental Update (10.14.6), 67310K [recommended] [restart]
   * Command Line Tools (macOS Mojave version 10.14) for Xcode-10.3
\tCommand Line Tools (macOS Mojave version 10.14) for Xcode (10.3), 199250K [recommended]
'''    
    self.assertEqual( [
      ( 'Command Line Tools (macOS Mojave version 10.14) for Xcode-10.3',
        'Command Line Tools (macOS Mojave version 10.14) for Xcode',
        { 'version': '10.3', 'size': '199250K', 'recommended': True },
       ) ,
      ( 'Safari14.0.1MojaveAuto-14.0.1',
        'Safari',
        { 'version': '14.0.1', 'size': '67518K', 'recommended': True },
       ) ,
      ( 'Safari14.0MojaveAuto-10.14.6',
        'macOS Supplemental Update',
        { 'version': '10.14.6', 'size': '67310K', 'recommended': True, 'restart': True },
       ) ,
      ( 'Security Update 2020-005-10.14.6',
        'Security Update 2020-005',
        { 'version': '10.14.6', 'size': '1633218K', 'recommended': True, 'restart': True },
       ) ,
    ], softwareupdater._parse_list_output(text) )

if __name__ == "__main__":
  unit_test.main()
