#!/usr/bin/env python
#-*- coding:utf-8 -*-
#
from bes.test import unit_test_helper

from bes.net.util.iwlist_scan_parser import iwlist_line, iwlist_scan_parser

class test_iwlist_scan_parser(unit_test_helper):

  test_file = __file__

  def test_iwlist_line_indent(self):
    self.assertEqual( 0, iwlist_line(0, 'foo').indent )
    self.assertEqual( 1, iwlist_line(0, ' foo').indent )
    self.assertEqual( 2, iwlist_line(0, '  foo').indent )
    self.assertEqual( 2, iwlist_line(0, '  foo ').indent )

  def test_iwlist_line_line_number(self):
    self.assertEqual( 0, iwlist_line(0, 'foo').line_number )
    self.assertEqual( 1, iwlist_line(1, 'foo').line_number )
    self.assertEqual( 2, iwlist_line(2, 'foo').line_number )

  def test_iwlist_line_text(self):
    self.assertEqual( 'foo', iwlist_line(0, 'foo').text )
    self.assertEqual( 'foo', iwlist_line(0, ' foo').text )
    self.assertEqual( 'foo', iwlist_line(0, '  foo').text )
    self.assertEqual( 'foo ', iwlist_line(0, '  foo ').text )

  def test_iwlist_line_original_text(self):
    self.assertEqual( 'foo', iwlist_line(0, 'foo').original_text )
    self.assertEqual( ' foo', iwlist_line(0, ' foo').original_text )
    self.assertEqual( '  foo', iwlist_line(0, '  foo').original_text )
    self.assertEqual( '  foo ', iwlist_line(0, '  foo ').original_text )

  def test_parse_list(self):
    f = iwlist_scan_parser._iwlist_scan_parser__parse_list
    self.assertEqual( { 'fruits': [ 'apple', 'orange' ] }, f('fruits (2):apple orange') )
    self.assertEqual( { 'fruits': [ 'apple', 'orange' ] }, f('fruits (2): apple orange') )
    self.assertEqual( { 'fruits': [ 'apple', 'orange' ] }, f('fruits (2): apple orange ') )
    self.assertEqual( { 'fruits': [ 'apple', 'orange' ] }, f(' fruits (2): apple orange ') )
    self.assertEqual( { 'fruits': [ 'apple', 'orange' ] }, f(' fruits(2): apple orange ') )
    self.assertEqual( { 'fruits': [ 'apple', 'orange' ] }, f(' fruits(2) : apple orange ') )
    self.assertEqual( { 'fruits': [ 'apple' ] }, f('fruits (1):apple') )
    self.assertEqual( { 'fruits': 'apple' }, f('fruits:apple') )

  def xtest_parse(self):
    self.maxDiff = None
    data = self.data('test_data/iwlist_output.txt')
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
    self.assertEqual( expected, iwlist_scan_parser(data).parse() )

if __name__ == "__main__":
  unit_test_helper.main()
