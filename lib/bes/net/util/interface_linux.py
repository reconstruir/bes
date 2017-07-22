#!/usr/bin/env python
#-*- coding:utf-8 -*-

from interface_base import interface_base

class interface_linux(interface_base):

  def get_interfaces(self):
    'Return a list of interfaces in this computer.'
    result = []
    lines = open('/proc/net/dev', 'r').read().strip().split('\n')[2:]
    for line in lines:
      result.append(line.partition(':')[0].strip())
    return result
