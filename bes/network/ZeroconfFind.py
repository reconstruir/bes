#!/usr/bin/env python
#-*- coding:utf-8 -*-

try:
  import dbus, gobject, avahi
  from dbus import DBusException
  from dbus.mainloop.glib import DBusGMainLoop
except:
  print 'Error: No avahi or dbus found.'

from threading import Thread, Lock, Timer
from Queue import Queue, Empty as QueueEmptyException

from bes.common import ObjectUtil, Network

class ZeroconfFind(Thread):
  'A class to find a zerconf service.'

  def __init__(self, stype):
    gobject.threads_init()
    super(ZeroconfFind, self).__init__()
    self.daemon = True
    self._stype = stype
    self._queue = Queue()
    self._timer = None
    self._result = []

  def run(self):

    def service_resolved(*args):
      result = ObjectUtil.make('ZerconfFindResult', {
        'name': str(args[2]),
        'host': str(args[5]),
        'address': str(args[7]),
        'port': int(args[8]),
        'local': str(args[4]),
      })
      if result.local == 'local' and Network.address_is_virtual(result.address):
        return
        
      #print 'service resolved: %s\n' % (result)
      self._result.append(result)

      if self._timer:
        self._timer.cancel()

      def _done():
        self._queue.put(self._result, block = False, timeout = None)

      self._timer = Timer(0.250, _done)
      self._timer.start()
  
    def print_error(*args):
      print 'error_handler'
      print args[0]
  
    def myhandler(interface, protocol, name, stype, domain, flags):

      # Could skip local service
      if flags & avahi.LOOKUP_RESULT_LOCAL:
        pass
  
      server.ResolveService(interface,
                            protocol,
                            name,
                            stype, 
                            domain,
                            avahi.PROTO_INET,
                            dbus.UInt32(0), 
                            reply_handler = service_resolved,
                            error_handler = print_error)
  
    loop = DBusGMainLoop()
  
    bus = dbus.SystemBus(mainloop = loop)
  
    server = dbus.Interface( bus.get_object(avahi.DBUS_NAME, '/'),
            'org.freedesktop.Avahi.Server')
  
    sb = server.ServiceBrowserNew(avahi.IF_UNSPEC,
                                  avahi.PROTO_INET,
                                  self._stype,
                                  'local',
                                  dbus.UInt32(0))
    sbrowser = dbus.Interface(bus.get_object(avahi.DBUS_NAME, sb),
                              avahi.DBUS_INTERFACE_SERVICE_BROWSER)
  
    sbrowser.connect_to_signal("ItemNew", myhandler)
    self._main_loop = gobject.MainLoop()
    self._main_loop.run()
  
  def find(self, timeout = None):
    self.start()

    try:
      result = self._queue.get(block = True, timeout = timeout)
      self._queue.task_done()
    except QueueEmptyException, ex:
      result = []
      
    self._main_loop.quit()
    self.join()
    return result

if __name__ == '__main__':
  stype = '_caca._tcp'
  finder = ZeroconfFind(stype)
  services = finder.find(timeout = 4.0)
  for service in services:
    print "found service: %s\n" % (service)
