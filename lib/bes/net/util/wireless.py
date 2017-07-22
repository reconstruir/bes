#!/usr/bin/env python
#-*- coding:utf-8 -*-

import platform, time

class wireless(object):
  'Top level class for dealing with wireless networks.'

  plat_name = platform.system()
  if plat_name == 'Darwin':
    from wireless_darwin import wireless_darwin
    _wireless_impl = wireless_darwin()
  elif plat_name == 'Linux':
    from wireless_linux import wireless_linux
    _wireless_impl = wireless_linux()
  else:
    raise RuntimeError('No wireless implementation found for platform: %s' % (plat_name))

  @classmethod
  def scan(clazz, interface, timeout = 1.0):
    'Scan for wireless networks.'
    start_time = time.time()
    while True:
      elapsed_time = time.time() - start_time
      if elapsed_time > timeout:
        raise RuntimeError('Timed out trying to scan for wireless networks.')
      result = clazz._wireless_impl.scan(interface)
      if len(result) > 0:
        return sorted(result, key = lambda item: item.ssid.lower())
