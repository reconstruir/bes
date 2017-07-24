#!/usr/bin/env python
#-*- coding:utf-8 -*-

from wireless_base import wireless_base, wireless_network
from iwlist_scan_parser import iwlist_scan_parser

from collections import namedtuple
from bes.fs import file_path
from bes.common import Shell, string_util
from mac_address import mac_address

class wireless_linux(wireless_base):

  def scan(self, interface):
    'Scan for wireless networks using iwlist.'
    rv = Shell.execute('iwlist %s scanning' % (interface))
    parser = iwlist_scan_parser(rv.stdout)
    d = parser.parse()
    if not d:
      return []
    assert len(d) == 1
    cells = d[0].get('cells', None)
    if not cells:
      return []
    result = []
    for cell in cells:
      age = None
      ap_mode = cell['mode']
      beacon_int = None
      address = cell['address']
      channel = cell['channel']
      noise = None
      signal_strength = cell['signal_level'].replace('dBm', '').strip()
      ssid = cell['essid']
      wn = wireless_network(age, ap_mode, beacon_int, address, channel, noise, signal_strength, ssid)
      result.append(wn)
    return result
