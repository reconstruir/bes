#!/usr/bin/env python
#-*- coding:utf-8 -*-

from bes.common import tuple_util, Shell

import os, platform, re, unittest, urllib2

class Network(object):
  'Network'

  plat_name = platform.system()
  if plat_name == 'Darwin':
    from interface_darwin import interface_darwin
    _interface_impl = interface_darwin()
  elif plat_name == 'Linux':
    from interface_linux import interface_linux
    _interface_impl = interface_linux()
  else:
    raise RuntimeError('No interface implementation found for platform: %s' % (plat_name))

  if plat_name == 'Darwin':
    from wireless_darwin import wireless_darwin
    _wireless_impl = wireless_darwin()
  elif plat_name == 'Linux':
    from wireless_linux import wireless_linux
    _wireless_impl = wireless_linux()
  else:
    raise RuntimeError('No interface implementation found for platform: %s' % (plat_name))

  @classmethod
  def get_interfaces(clazz, include_virtual = False):
    'Return a list of network interfaces.'
    result = clazz._interface_impl.get_interfaces()
    if include_virtual:
      return result
    return [ i for i in result if not clazz.is_virtual(i) ]

  @classmethod
  def wireless_scan(clazz, interface):
    'Scan for wireless networks.'
    result = clazz._wireless_impl.scan(interface)
    return result

  @classmethod
  def exists(clazz, iface):
    'Return ifocnfig for the given interface.'
    return iface in clazz.get_interfaces(True)

  @classmethod
  def ifconfig(clazz, iface):
    'Return ifocnfig for the given interface.'
    if not clazz.exists(iface):
      raise RuntimeError('Interface %s does not exist' % (iface))
    r = Shell.execute(['ifconfig', iface])
    def __section(exp, s):
      try:
        x = re.split(exp, s)
        return re.split(exp, s)[1]
      except:
        return None

    def __parse_mac_netmask(n):
      if not n or len(n) != 10:
        return None
      parts = []
      parts.append(str(int(n[2:4], 16)))
      parts.append(str(int(n[4:6], 16)))
      parts.append(str(int(n[6:8], 16)))
      parts.append(str(int(n[8:10], 16)))
      return '.'.join(parts)

    if platform.system() == 'Darwin':
      mac = __section('ether (\w\w:\w\w:\w\w:\w\w:\w\w:\w\w)', r.stdout)
      ip = __section('inet (\d*\.\d*\.\d*\.\d*\w)', r.stdout)
      broadcast = __section('broadcast (\d*\.\d*\.\d*\.\d*\w)', r.stdout)
      netmask = __parse_mac_netmask(__section('netmask (0x\w\w\w\w\w\w\w\w)', r.stdout))
    else:
      mac = __section('HWaddr (\w\w:\w\w:\w\w:\w\w:\w\w:\w\w)', r.stdout) \
        or __section('ether\s+(\w\w:\w\w:\w\w:\w\w:\w\w:\w\w)', r.stdout)
      ip = __section('inet addr:(\d*\.\d*\.\d*\.\d*\w)', r.stdout) \
        or __section('inet\s+(\d*\.\d*\.\d*\.\d*\w)', r.stdout)
      broadcast = __section('Bcast:(\d*\.\d*\.\d*\.\d*\w)', r.stdout) \
        or __section('broadcast\s+(\d*\.\d*\.\d*\.\d*\w)', r.stdout)
      netmask = __section('Mask:(\d*\.\d*\.\d*\.\d*\w)', r.stdout) \
        or __section('netmask\s+(\d*\.\d*\.\d*\.\d*\w)', r.stdout)
    return tuple_util.dict_to_named_tuple('Iface', { 'mac': mac, 'ip': ip, 'broadcast': broadcast, 'netmask': netmask })

  @classmethod
  def get_mac_address(clazz, iface):
    'Return the mac address for the interface.'
    return clazz.ifconfig(iface).mac

  @classmethod
  def is_virtual(clazz, iface):
    'Return True if the interface is virtual.'
    return iface.startswith('lo') or iface.startswith('vm')

  @classmethod
  def address_is_virtual(clazz, address):
    'Return True if the given ip address is virtual.'
    ifaces = clazz.get_interfaces(include_virtual = True)
    for iface in ifaces:
      if clazz.is_virtual(iface) and clazz.ifconfig(iface).ip == address:
        return True
    return False

  @classmethod
  def ping(clazz, ip, count = 1, timeout = 1):
    'Ping the ip address and return True if it is reachable.'
    cmd = [ 'ping' ]
    cmd.append('-c')
    cmd.append(str(count))
    cmd.append('-W')
    cmd.append(str(timeout))
    cmd.append(ip)
    r = Shell.execute(cmd)
    return r.exit_code == 0

  @classmethod
  def parse_host_port(clazz, s, default_port = 0):
    'Parse a host and port string in the form of host:port.'
    x = s.partition(':')

    try:
      port = int(x[2])
    except:
      port = default_port

    return (x[0] or 'localhost', port)

  @classmethod
  def get_ip_address(clazz):
    iface = clazz.get_interfaces()[0]
    ifconfig = clazz.ifconfig(iface)
    return ifconfig.ip

  @classmethod
  def get_external_ip_address(clazz):
    return urllib2.urlopen('http://ipinfo.io/ip').read().strip()
