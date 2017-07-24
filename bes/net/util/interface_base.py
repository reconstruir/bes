#!/usr/bin/env python
#-*- coding:utf-8 -*-

from abc import abstractmethod
from collections import namedtuple

Item = namedtuple('interface', 'name,mac_address,is_virtual,is_wireless')

class interface_base(object):

  @abstractmethod
  def get_interfaces(self):
    'Return a list of interfaces in this computer.'
    assert False
