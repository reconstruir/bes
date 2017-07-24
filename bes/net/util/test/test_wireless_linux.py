#!/usr/bin/env python
#-*- coding:utf-8 -*-
#
from bes.test import unit_test_helper
from bes.net.util import Network

from bes.net.util.wireless_linux import wireless_linux

class test_wireless_linux(unit_test_helper):

  test_file = __file__

  def xtest_parse_iwlist_output_one_cell(self):
    data = self.data('test_data/iwlist_output_one_cell.txt')
    expected = {
      'name': 'Cell 18',
      'tsf': '000000b50fc07180',
      'bitrates': ['1 Mb/s', '2 Mb/s', '5.5 Mb/s', '11 Mb/s', '6 Mb/s', '9 Mb/s', '12 Mb/s', '18 Mb/s', '24 Mb/s', '36 Mb/s', '48 Mb/s', '54 Mb/s'],
      'encryption_key': 'on',
      'signal_level': '-63 dBm',
      'frequency': '2.462 GHz',
      'essid': '',
      'address': '9e:34:26:88:38:5a',
      'ie': [ 
        ( 'IEEE 802.11i/WPA2 Version 1', {'Pairwise Ciphers': ['CCMP', 'TKIP'], 'Authentication Suites': ['PSK'], 'Group Cipher': 'TKIP'} ),
        ( 'WPA Version 1', {'Pairwise Ciphers': ['CCMP', 'TKIP'], 'Authentication Suites': ['PSK'], 'Group Cipher': 'TKIP'} ),
      ],
      'Last beacon': '16120ms ago',
      'quality': '47/70',
      'channel': '11',
      'mode': 'Master'
    }
    actual = wireless_linux().parse_iwlist_output_one_cell(data)
    self.assertEqual( expected, actual )

  def xtest_count_indent(self):
    wl = wireless_linux()
    self.assertEqual( 0, wl.count_indent('foo') )
    self.assertEqual( 1, wl.count_indent(' foo') )
    self.assertEqual( 2, wl.count_indent('  foo') )

  def xtest_expand_line(self):
    wl = wireless_linux()
    self.assertEqual( '  foo', wl.expand_line(wireless_linux.line(2, 'foo')) )

  def xtest_determine_line(self):
    wl = wireless_linux()
    self.assertEqual( wl.line(0, 'foo' ), wl.determine_line('foo') )
    self.assertEqual( wl.line(1, 'foo' ), wl.determine_line(' foo') )
    self.assertEqual( wl.line(2, 'foo bar' ), wl.determine_line('  foo bar') )
    self.assertEqual( wl.line(2, 'foo bar ' ), wl.determine_line('  foo bar ') )

  def xtest_parse_list(self):
    wl = wireless_linux()
    self.assertEqual( { 'fruits': [ 'apple', 'orange' ] }, wl.parse_list('fruits (2):apple orange') )
    self.assertEqual( { 'fruits': [ 'apple', 'orange' ] }, wl.parse_list('fruits (2): apple orange') )
    self.assertEqual( { 'fruits': [ 'apple', 'orange' ] }, wl.parse_list('fruits (2): apple orange ') )
    self.assertEqual( { 'fruits': [ 'apple', 'orange' ] }, wl.parse_list(' fruits (2): apple orange ') )
    self.assertEqual( { 'fruits': [ 'apple', 'orange' ] }, wl.parse_list(' fruits(2): apple orange ') )
    self.assertEqual( { 'fruits': [ 'apple', 'orange' ] }, wl.parse_list(' fruits(2) : apple orange ') )
    self.assertEqual( { 'fruits': [ 'apple' ] }, wl.parse_list('fruits (1):apple') )
    self.assertEqual( { 'fruits': 'apple' }, wl.parse_list('fruits:apple') )
    
  def xtest_cell_collect_lines(self):
    text =\
'''

  root a=6
    foo b=9
    fruits
      orange a=5; b=6; c=7
      apple d=8; e=9; f=10
      kiwi g=11
    baz

    vegetables
      potato
      yam
      carrot
    bread

'''  
    expected = [
      [ 'root a=6' ],
      [ 'foo b=9' ],
      [ 'fruits', 'orange a=5; b=6; c=7', 'apple d=8; e=9; f=10', 'kiwi g=11' ],
      [ 'baz' ],
      [ 'vegetables', 'potato', 'yam', 'carrot' ],
      [ 'bread' ],
    ]
    wl = wireless_linux()
    self.assertEqual( expected, wl.cell_collect_lines(text) )

  def xtest_radio_collect_cells(self):
    text =\
'''
  Cell 01
    a
    b
    c

  Cell 02
    x
    y
    z
  Cell 03
    i
    j
    k
'''  

    expected = [
'''  Cell 01
    a
    b
    c''',
'''  Cell 02
    x
    y
    z''',
'''  Cell 03
    i
    j
    k'''
  ]      

    wl = wireless_linux()
    self.assertEqual( expected, wl.radio_collect_cells(text) )

  def xtest_scan_collect_radios(self):
    text =\
'''
r1        No scan results

r2        Scan completed :
          Cell 01 - a: y1
                    c:1
                    f:x
          Cell 02 - a: y2
                    c:1
                    f:x
                    b: d e f
                       h i g
          Cell 03 - a: y3
                    c:1
                    f:x

r3        Scan completed :
          Cell 01 - a: y4
                    c:1
                    f:x
          Cell 02 - a: y5
                    c:1
                    f: x
'''  

    expected = [
      '''r1        No scan results''',
      '''r2        Scan completed :
          Cell 01 - a: y1
                    c:1
                    f:x
          Cell 02 - a: y2
                    c:1
                    f:x
                    b: d e f
                       h i g
          Cell 03 - a: y3
                    c:1
                    f:x''',
      '''r3        Scan completed :
          Cell 01 - a: y4
                    c:1
                    f:x
          Cell 02 - a: y5
                    c:1
                    f: x'''
    ]      

    wl = wireless_linux()
    self.assertEqual( expected, wl.scan_collect_radios(text) )

if __name__ == "__main__":
  unit_test_helper.main()
