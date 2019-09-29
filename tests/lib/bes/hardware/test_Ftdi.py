#!/usr/bin/env python3
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import unittest
from bes.hardware.Ftdi import Ftdi

class TestFtdi(unittest.TestCase):

  def test_find_devices(self):
    devices = Ftdi.find_devices()
    for device in devices:
      print('DEVICE: ', device)

if __name__ == "__main__":
  unittest.main()
