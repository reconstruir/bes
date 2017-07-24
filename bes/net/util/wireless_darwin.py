#!/usr/bin/env python
#-*- coding:utf-8 -*-

from wireless_base import wireless_base, wireless_network
  
import plistlib
from bes.fs import file_path
from bes.common import Shell, string_util
from mac_address import mac_address

class wireless_darwin(wireless_base):

  __POSSIBLE_EXES = [ 'airport', '/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport' ]

  # The names airport uses are a bit confusing to humans
  __FIELD_MAP = {
    'address': 'bssid',
    'signal_strength': 'rssi',
    'ssid': 'ssid_str',
  }
  
  def scan(self, interface):
    'Scan for wireless networks using the mac airport command line tool.'
    rv = Shell.execute('airport %s -s -x' % (interface))
    devices = plistlib.readPlistFromString(rv.stdout)
    result = []
    for device in devices:
      fields = []
      for key in wireless_network._fields:
        value = device[self.__FIELD_MAP.get(key, key).upper()]
        if key == 'address':
          value = mac_address.normalize_mac_address(value)
        fields.append(value)
      network = wireless_network(*fields)
      result.append(network)
    return result
  
  def __find_airport(self):
    'Find the airport utility and return its path or None if not found.'
    for exe in self.__POSSIBLE_EXES:
      try:
        return file_path.which(exe)
      except:
        pass
    return None
