#!/usr/bin/env python
#-*- coding:utf-8 -*-

# =========================================================================
# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# =========================================================================

import unittest

import os, os.path as path, sys, re

import pprint

global _have_udev
try:
  import pyudev
  _have_udev = True
except:
  _have_udev = False

class Ftdi(object):

  @classmethod
  def find_devices(clazz, vendor_string = None):
    if not _have_udev:
      print('This system does not have pyudev')
      return []
    context = pyudev.Context()
    ftdi_devices = list(context.list_devices())
    devices = []
    for ftdi_device in ftdi_devices:
      if ftdi_device.device_node and ftdi_device.sys_name.find('ttyUSB') >= 0:
        devices.append(ftdi_device)

    result = []
    for device in devices:
      info = clazz.parse_device_links(device.device_links)
      skip = False
      if vendor_string:
        if not (info[0].find(vendor_string) >= 0):
          skip = True
      if not skip:
        result.append( ( info[0], info[1], str(device.device_node) ) )
        if info[0] == 'Serial':
          print(" INFO: ", pprint.pformat(info))
          print("ITEMS: ", pprint.pformat(device.items()))
    return result


  @classmethod
  def parse_device_link(clazz, device_link):
    'Parse a device link to figure out the vendor and serial number'
    x = re.split('.*-(.*)_(.*)-if.*-port.*', device_link)
    if len(x) != 4:
      return None
    return ( str(x[1]), str(x[2]) )

  @classmethod
  def parse_device_links(clazz, device_links):
    'Parse a device link to figure out the vendor and serial number'
    for device_link in device_links:
      p = clazz.parse_device_link(device_link)
      if p:
        return p
    return None
