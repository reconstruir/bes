#!/usr/bin/env python
#-*- coding:utf-8 -*-

try:
  import avahi, dbus
except:
  print 'Error: No avahi or dbus found.'

class ZeroconfPublish(object):
  'A simple class to publish a network service with zeroconf using avahi.'

  def __init__(self, name, port, stype, domain = '', host = '', text = ''):
    self.name = name
    self.stype = stype
    self.domain = domain
    self.host = host
    self.port = port
    self.text = text

  def publish(self):
    bus = dbus.SystemBus()
    server = dbus.Interface(bus.get_object(avahi.DBUS_NAME,
                                           avahi.DBUS_PATH_SERVER),
                            avahi.DBUS_INTERFACE_SERVER)

    g = dbus.Interface(bus.get_object(avahi.DBUS_NAME, server.EntryGroupNew()),
                       avahi.DBUS_INTERFACE_ENTRY_GROUP)

    g.AddService(avahi.IF_UNSPEC, avahi.PROTO_UNSPEC,dbus.UInt32(0),
                 self.name, self.stype, self.domain, self.host,
                 dbus.UInt16(self.port), self.text)

    g.Commit()
    self.group = g

  def unpublish(self):
    self.group.Reset()

if __name__ == '__main__':
  stype = '_caca._tcp'
  service = ZeroconfPublish('TestService', 9999, stype)
  service.publish()
  raw_input('Press any key to unpublish the service ')
  service.unpublish()
