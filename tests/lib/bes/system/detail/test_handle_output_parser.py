#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test

from bes.system.detail.handle_output_parser import handle_output_parser as P

class test_handle_output_parser(unit_test):

  def test__parse_header(self):
    self.assertEqual( ( 'conhost.exe', 10320, 'BEDROCK\\fred' ),
                      P._parse_header(r'conhost.exe pid: 10320 BEDROCK\fred') )

  def test__parse_header_unable_to_open_process(self):
    self.assertEqual( ( 'System', 4, None ),
                      P._parse_header(r'System pid: 4 \<unable to open process>') )

  def test__parse_section(self):
    text = r'''
conhost.exe pid: 10320 BEDROCK\fred
  130: File          C:\Windows\System32\en-US\Conhost.exe.mui
  1B0: Section       \Windows\Theme3773140654
  1C8: File          C:\Windows\Fonts\StaticCache.dat
  1D0: Section       \Sessions\1\BaseNamedObjects\SessionImmersiveColorPreference
  1DC: File          C:\Windows\System32\en-US\user32.dll.mui
  1FC: Section       \Sessions\1\BaseNamedObjects\windows_shell_global_counters
'''
    expected = (
      ( 'conhost.exe', 10320, 'BEDROCK\\fred' ),
      [
        ( 304, 'File', r'C:\Windows\System32\en-US\Conhost.exe.mui' ),
        ( 432, 'Section', r'\Windows\Theme3773140654' ),
        ( 456, 'File', r'C:\Windows\Fonts\StaticCache.dat' ),
        ( 464, 'Section', r'\Sessions\1\BaseNamedObjects\SessionImmersiveColorPreference' ),
        ( 476, 'File', r'C:\Windows\System32\en-US\user32.dll.mui' ),
        ( 508, 'Section', r'\Sessions\1\BaseNamedObjects\windows_shell_global_counters' ),
      ]
    )
    actual = P._parse_section(text)
    self.assertEqual( expected, actual )

  def test__parse_section_unable_to_open_process(self):
    text = r'''
System pid: 4 \<unable to open process>'
'''

    expected = ( ( 'System', 4, None ), [] )
    actual = P._parse_section(text)
    self.assertEqual( expected, actual )
    
  def test_parse_handle_output_one_line(self):
    text = r'''
  130: File          C:\Windows\System32\en-US\Conhost.exe.mui
  1B0: Section       \Windows\Theme3773140654
  1C8: File          C:\Windows\Fonts\StaticCache.dat
  1D0: Section       \Sessions\1\BaseNamedObjects\SessionImmersiveColorPreference
  1DC: File          C:\Windows\System32\en-US\user32.dll.mui
  1FC: Section       \Sessions\1\BaseNamedObjects\windows_shell_global_counters
'''
    expected = [
      (
        None,
        [
          ( 304, 'File', r'C:\Windows\System32\en-US\Conhost.exe.mui' ),
          ( 432, 'Section', r'\Windows\Theme3773140654' ),
          ( 456, 'File', r'C:\Windows\Fonts\StaticCache.dat' ),
          ( 464, 'Section', r'\Sessions\1\BaseNamedObjects\SessionImmersiveColorPreference' ),
          ( 476, 'File', r'C:\Windows\System32\en-US\user32.dll.mui' ),
          ( 508, 'Section', r'\Sessions\1\BaseNamedObjects\windows_shell_global_counters' ),
        ]
      ),
    ]
    actual = P.parse_handle_output(text)
    self.assertEqual( expected, actual )
    
  def test_parse_handle_output_many_lines(self):
    text = r'''
------------------------------------------------------------------------------
System pid: 4 \<unable to open process>
------------------------------------------------------------------------------
smss.exe pid: 324 \<unable to open process>
------------------------------------------------------------------------------
conhost.exe pid: 10320 BEDROCK\fred
  130: File          C:\Windows\System32\en-US\Conhost.exe.mui
  1B0: Section       \Windows\Theme3773140654
  1C8: File          C:\Windows\Fonts\StaticCache.dat
  1D0: Section       \Sessions\1\BaseNamedObjects\SessionImmersiveColorPreference
  1DC: File          C:\Windows\System32\en-US\user32.dll.mui
  1FC: Section       \Sessions\1\BaseNamedObjects\windows_shell_global_counters
------------------------------------------------------------------------------
svchost.exe pid: 9572 \<unable to open process>
'''

    x = r'''
------------------------------------------------------------------------------
cmd.exe pid: 8544 BEDROCK\fred
   54: File          C:\Windows\System32\en-US\KernelBase.dll.mui
  118: File          C:\Windows\System32\en-US\cmd.exe.mui
  12C: Section       \Sessions\1\BaseNamedObjects\ConEmuAppMapping.00830422
  130: Section       \Sessions\1\BaseNamedObjects\ConEmuFileMapping.00830422
  160: File          C:\Users\fred\something
  170: Section       \Sessions\1\BaseNamedObjects\Console_annotationInfo_20_5103c0
  1BC: File          C:\Users\fred\something\handle_all.txt
'''
    expected = [
      (
        ( 'System', 4, None ),
        []
      ),
      (
        ( 'smss.exe', 324, None ),
        []
      ),
      (
        ( 'conhost.exe', 10320, 'BEDROCK\\fred' ),
        [
          ( 304, 'File', r'C:\Windows\System32\en-US\Conhost.exe.mui' ),
          ( 432, 'Section', r'\Windows\Theme3773140654' ),
          ( 456, 'File', r'C:\Windows\Fonts\StaticCache.dat' ),
          ( 464, 'Section', r'\Sessions\1\BaseNamedObjects\SessionImmersiveColorPreference' ),
          ( 476, 'File', r'C:\Windows\System32\en-US\user32.dll.mui' ),
          ( 508, 'Section', r'\Sessions\1\BaseNamedObjects\windows_shell_global_counters' ),
        ]
      ),
      (
        ( 'svchost.exe', 9572, None ),
        []
      ),
    ]
    actual = P.parse_handle_output(text)
    self.assert_json_object_equal( expected, actual )
    
if __name__ == '__main__':
  unit_test.main()
