#!/usr/bin/env python
#-*- coding:utf-8 -*-

from abc import abstractmethod
from collections import namedtuple

Item = namedtuple('interface', 'name,mac_address,is_virtual,is_wireless')

wireless_network = namedtuple('wireless_network', 'age,ap_mode,beacon_int,address,channel,noise,signal_strength,ssid')

class wireless_base(object):

  @abstractmethod
  def scan(self, interface):
    'Return a list of interfaces in this computer.'
    assert False
