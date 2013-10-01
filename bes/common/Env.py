#!/usr/bin/env python
#-*- coding:utf-8 -*-

from Network import Network

class Env(object):
  'Env'

  @classmethod
  def __is_home(clazz, ip):
    return ip.startswith('172.30.1')

  @classmethod
  def __is_work(clazz, ip):
    return Network.ping('svn.tango.corp')

  @classmethod
  def where_am_i(clazz):
    ifaces = Network.get_interfaces()
    ifaces = [ iface for iface in ifaces if not Network.is_virtual(iface) ]
    configs = [ Network.ifconfig(iface) for iface in ifaces ]
    ips = [ config.ip for config in configs if config.ip ]
    for ip in ips:
      if clazz.__is_home(ip):
        return 'home'
      elif clazz.__is_work(ip):
        return 'work'
    return 'work'
