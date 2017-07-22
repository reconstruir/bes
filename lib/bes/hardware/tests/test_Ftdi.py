#!/usr/bin/env python
#-*- coding:utf-8 -*-
#
import unittest
from bes.hardware import Ftdi

class TestFtdi(unittest.TestCase):

  def test_find_devices(self):
    devices = Ftdi.find_devices()
    for device in devices:
      print 'DEVICE: ', device

if __name__ == "__main__":
  unittest.main()
