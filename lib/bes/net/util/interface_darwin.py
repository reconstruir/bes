#!/usr/bin/env python
#-*- coding:utf-8 -*-

from interface_base import interface_base

class interface_darwin(interface_base):

  def get_interfaces(self):
    'Return a list of interfaces in this computer.'
    return [ 'en0', 'en1' ]
